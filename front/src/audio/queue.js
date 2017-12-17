import Vue from 'vue'
import _ from 'lodash'

import logger from '@/logging'
import cache from '@/cache'
import config from '@/config'
import Audio from '@/audio'
import backend from '@/audio/backend'
import radios from '@/radios'
import url from '@/utils/url'
import auth from '@/auth'

class Queue {
  constructor (options = {}) {
    logger.default.info('Instanciating queue')
    this.previousQueue = cache.get('queue')
    this.tracks = []
    this.currentIndex = -1
    this.currentTrack = null
    this.ended = true
    this.state = {
      looping: 0, // 0 -> no, 1 -> on  track, 2 -> on queue
      volume: cache.get('volume', 0.5)
    }
    this.audio = {
      state: {
        startLoad: false,
        failed: false,
        try: 3,
        tried: 0,
        playing: false,
        paused: false,
        playbackRate: 1.0,
        progress: 0,
        currentTime: 0,
        duration: 0,
        volume: this.state.volume,
        loaded: '0',
        durationTimerFormat: '00:00',
        currentTimeFormat: '00:00',
        lastTimeFormat: '00:00'
      }
    }
  }

  cache () {
    let cached = {
      tracks: this.tracks.map(track => {
        // we keep only valuable fields to make the cache lighter and avoid
        // cyclic value serialization errors
        let artist = {
          id: track.artist.id,
          mbid: track.artist.mbid,
          name: track.artist.name
        }
        return {
          id: track.id,
          title: track.title,
          mbid: track.mbid,
          album: {
            id: track.album.id,
            title: track.album.title,
            mbid: track.album.mbid,
            cover: track.album.cover,
            artist: artist
          },
          artist: artist,
          files: track.files
        }
      }),
      currentIndex: this.currentIndex
    }
    cache.set('queue', cached)
  }

  restore () {
    let cached = cache.get('queue')
    if (!cached) {
      return false
    }
    logger.default.info('Restoring previous queue...')
    this.tracks = cached.tracks
    this.play(cached.currentIndex)
    this.previousQueue = null
    return true
  }
  removePrevious () {
    this.previousQueue = undefined
    cache.remove('queue')
  }
  setVolume (newValue) {
    newValue = Math.min(newValue, 1)
    newValue = Math.max(newValue, 0)
    this.state.volume = newValue
    if (this.audio.setVolume) {
      this.audio.setVolume(newValue)
    } else {
      this.audio.state.volume = newValue
    }
    cache.set('volume', newValue)
  }
  incrementVolume (value) {
    this.setVolume(this.state.volume + value)
  }
  reorder (oldIndex, newIndex) {
    // called when the user uses drag / drop to reorder
    // tracks in queue
    if (oldIndex === this.currentIndex) {
      this.currentIndex = newIndex
      return
    }
    if (oldIndex < this.currentIndex && newIndex >= this.currentIndex) {
      // item before was moved after
      this.currentIndex -= 1
    }
    if (oldIndex > this.currentIndex && newIndex <= this.currentIndex) {
      // item after was moved before
      this.currentIndex += 1
    }
  }

  append (track, index, skipPlay) {
    this.previousQueue = null
    index = index || this.tracks.length
    if (index > this.tracks.length - 1) {
      // we simply push to the end
      this.tracks.push(track)
    } else {
      // we insert the track at given position
      this.tracks.splice(index, 0, track)
    }
    if (!skipPlay) {
      this.resumeQueue()
    }
    this.cache()
  }

  appendMany (tracks, index) {
    logger.default.info('Appending many tracks to the queue', tracks.map(e => { return e.title }))
    let self = this
    if (this.tracks.length === 0) {
      index = 0
    } else {
      index = index || this.tracks.length
    }
    tracks.forEach((t) => {
      self.append(t, index, true)
      index += 1
    })
    this.resumeQueue()
  }

  resumeQueue () {
    if (this.ended | this.errored) {
      this.next()
    }
  }

  populateFromRadio () {
    if (!radios.running) {
      return
    }
    var self = this
    radios.fetch().then((response) => {
      logger.default.info('Adding track to queue from radio')
      self.append(response.data.track)
    }, (response) => {
      logger.default.error('Error while adding track to queue from radio')
    })
  }

  clean () {
    this.stop()
    radios.stop()
    this.tracks = []
    this.currentIndex = -1
    this.currentTrack = null
    // so we replay automatically on next track append
    this.ended = true
  }

  cleanTrack (index) {
    // are we removing current playin track
    let current = index === this.currentIndex
    if (current) {
      this.stop()
    }
    if (index < this.currentIndex) {
      this.currentIndex -= 1
    }
    this.tracks.splice(index, 1)
    if (current) {
      // we play next track, which now have the same index
      this.play(index)
    }
    if (this.currentIndex === this.tracks.length - 1) {
      this.populateFromRadio()
    }
  }

  stop () {
    if (this.audio.pause) {
      this.audio.pause()
    }
    if (this.audio.destroyed) {
      this.audio.destroyed()
    }
  }
  play (index) {
    let self = this
    let currentIndex = index
    let currentTrack = this.tracks[index]

    if (this.audio.destroyed) {
      logger.default.debug('Destroying previous audio...', index - 1)
      this.audio.destroyed()
    }

    if (!currentTrack) {
      return
    }

    this.currentIndex = currentIndex
    this.currentTrack = currentTrack

    this.ended = false
    this.errored = false
    let file = this.currentTrack.files[0]
    if (!file) {
      this.errored = true
      return this.next()
    }
    let path = backend.absoluteUrl(file.path)
    if (auth.user.authenticated) {
      // we need to send the token directly in url
      // so authentication can be checked by the backend
      // because for audio files we cannot use the regular Authentication
      // header
      path = url.updateQueryString(path, 'jwt', auth.getAuthToken())
    }

    let audio = new Audio(path, {
      preload: true,
      autoplay: true,
      rate: 1,
      loop: false,
      volume: this.state.volume,
      onEnded: this.handleAudioEnded.bind(this),
      onError: function (src) {
        self.errored = true
        self.next()
      }
    })
    this.audio = audio
    audio.updateHook('playState', function (e) {
      // in some situations, we may have a race condition, for example
      // if the user spams the next / previous buttons, with multiple audios
      // playing at the same time. To avoid that, we ensure the audio
      // still matches de queue current audio
      if (audio !== self.audio) {
        logger.default.debug('Destroying duplicate audio')
        audio.destroyed()
      }
    })
    if (this.currentIndex === this.tracks.length - 1) {
      this.populateFromRadio()
    }
    this.cache()
  }

  handleAudioEnded (e) {
    this.recordListen(this.currentTrack)
    if (this.state.looping === 1) {
      // we loop on the same track
      logger.default.info('Looping on the same track')
      return this.play(this.currentIndex)
    }
    if (this.currentIndex < this.tracks.length - 1) {
      logger.default.info('Audio track ended, playing next one')
      return this.next()
    } else {
      logger.default.info('We reached the end of the queue')
      if (this.state.looping === 2) {
        logger.default.info('Going back to the beginning of the queue')
        return this.play(0)
      } else {
        this.ended = true
      }
    }
  }

  recordListen (track) {
    let url = config.API_URL + 'history/listenings/'
    let resource = Vue.resource(url)
    resource.save({}, {'track': track.id}).then((response) => {}, (response) => {
      logger.default.error('Could not record track in history')
    })
  }

  previous () {
    if (this.currentIndex > 0) {
      this.play(this.currentIndex - 1)
    }
  }

  next () {
    if (this.currentIndex < this.tracks.length - 1) {
      logger.default.debug('Playing next track')
      this.play(this.currentIndex + 1)
    }
  }

  toggleLooping () {
    if (this.state.looping > 1) {
      this.state.looping = 0
    } else {
      this.state.looping += 1
    }
  }

  shuffle () {
    let tracks = this.tracks
    let shuffled = _.shuffle(tracks)
    this.clean()
    this.appendMany(shuffled)
  }

}

let queue = new Queue()

export default queue
