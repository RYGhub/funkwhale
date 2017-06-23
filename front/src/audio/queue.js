import logger from '@/logging'
import cache from '@/cache'
import config from '@/config'
import Audio from '@/audio'
import backend from '@/audio/backend'
import radios from '@/radios'
import Vue from 'vue'

class Queue {
  constructor (options = {}) {
    logger.default.info('Instanciating queue')
    this.previousQueue = cache.get('queue')
    this.tracks = []
    this.currentIndex = -1
    this.currentTrack = null
    this.ended = true
    this.state = {
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
    this.state.volume = newValue
    if (this.audio.setVolume) {
      this.audio.setVolume(newValue)
    } else {
      this.audio.state.volume = newValue
    }
    cache.set('volume', newValue)
  }
  append (track, index) {
    this.previousQueue = null
    index = index || this.tracks.length
    if (index > this.tracks.length - 1) {
      // we simply push to the end
      this.tracks.push(track)
    } else {
      // we insert the track at given position
      this.tracks.splice(index, 0, track)
    }
    if (this.ended) {
      this.play(this.currentIndex + 1)
    }
    this.cache()
  }

  appendMany (tracks, index) {
    let self = this
    index = index || this.tracks.length - 1
    tracks.forEach((t) => {
      self.append(t, index)
      index += 1
    })
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
    this.tracks = []
    this.currentIndex = -1
    this.currentTrack = null
  }

  cleanTrack (index) {
    if (index === this.currentIndex) {
      this.stop()
    }
    if (index < this.currentIndex) {
      this.currentIndex -= 1
    }
    this.tracks.splice(index, 1)
  }

  stop () {
    this.audio.pause()
    this.audio.destroyed()
  }
  play (index) {
    if (this.audio.destroyed) {
      logger.default.debug('Destroying previous audio...')
      this.audio.destroyed()
    }
    this.currentIndex = index
    this.currentTrack = this.tracks[index]
    this.ended = false
    let file = this.currentTrack.files[0]
    if (!file) {
      return this.next()
    }
    this.audio = new Audio(backend.absoluteUrl(file.path), {
      preload: true,
      autoplay: true,
      rate: 1,
      loop: false,
      volume: this.state.volume,
      onEnded: this.handleAudioEnded.bind(this)
    })
    if (this.currentIndex === this.tracks.length - 1) {
      this.populateFromRadio()
    }
    this.cache()
  }

  handleAudioEnded (e) {
    this.recordListen(this.currentTrack)
    if (this.currentIndex < this.tracks.length - 1) {
      logger.default.info('Audio track ended, playing next one')
      this.next()
    } else {
      logger.default.info('We reached the end of the queue')
      this.ended = true
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
      this.play(this.currentIndex + 1)
    }
  }

}

let queue = new Queue()

export default queue
