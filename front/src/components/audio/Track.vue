<template>
  <i />
</template>

<script>
import {mapState} from 'vuex'
import _ from '@/lodash'
import url from '@/utils/url'
import {Howl} from 'howler'

// import logger from '@/logging'

export default {
  props: {
    track: {type: Object},
    isCurrent: {type: Boolean, default: false},
    startTime: {type: Number, default: 0},
    autoplay: {type: Boolean, default: false}
  },
  data () {
    return {
      sourceErrors: 0,
      sound: null,
      isUpdatingTime: false,
      progressInterval: null
    }
  },
  mounted () {
    let self = this
    this.sound = new Howl({
      src: this.srcs.map((s) => { return s.url }),
      format: this.srcs.map((s) => { return s.type }),
      autoplay: false,
      loop: false,
      html5: true,
      preload: true,
      volume: this.volume,
      onend: function () {
        self.ended()
      },
      onunlock: function () {
        if (this.$store.state.player.playing) {
          self.sound.play()
        }
      },
      onload: function () {
        self.$store.commit('player/isLoadingAudio', false)
        self.$store.commit('player/resetErrorCount')
        self.$store.commit('player/errored', false)
        self.$store.commit('player/duration', self.sound.duration())
        let node = self.sound._sounds[0]._node;
        node.addEventListener('progress', () => {
          self.updateBuffer(node)
        })
      },
      onloaderror: function (sound, error) {
        console.log('Error while playing:', sound, error)
        self.$emit('errored', {sound, error})
      },
    })
    if (this.autoplay) {
      self.$store.commit('player/isLoadingAudio', true)
      this.sound.play()
      this.$store.commit('player/playing', true)
      this.observeProgress(true)
    }
  },
  destroyed () {
    this.observeProgress(false)
    this.sound.unload()
  },
  computed: {
    ...mapState({
      playing: state => state.player.playing,
      currentTime: state => state.player.currentTime,
      duration: state => state.player.duration,
      volume: state => state.player.volume,
      looping: state => state.player.looping
    }),
    srcs: function () {
      let sources = this.track.uploads.map(u => {
        return {
          type: u.extension,
          url: this.$store.getters['instance/absoluteUrl'](u.listen_url),
        }
      })
      // We always add a transcoded MP3 src at the end
      // because transcoding is expensive, but we want browsers that do
      // not support other codecs to be able to play it :)
      sources.push({
        type: 'mp3',
        url: url.updateQueryString(
          this.$store.getters['instance/absoluteUrl'](this.track.listen_url),
          'to',
          'mp3'
        )
      })
      if (this.$store.state.auth.authenticated) {
        // we need to send the token directly in url
        // so authentication can be checked by the backend
        // because for audio files we cannot use the regular Authentication
        // header
        sources.forEach(e => {
          e.url = url.updateQueryString(e.url, 'jwt', this.$store.state.auth.token)
        })
      }
      return sources
    },
    updateProgressThrottled () {
      return _.throttle(this.updateProgress, 250)
    }
  },
  methods: {
    updateBuffer (node) {
      // from https://github.com/goldfire/howler.js/issues/752#issuecomment-372083163
      let range = 0;
      let bf = node.buffered;
      let time = node.currentTime;
      try {
        while(!(bf.start(range) <= time && time <= bf.end(range))) {
          range += 1;
        }
      } catch (IndexSizeError) {
        return
      }
      let loadPercentage
      let start =  bf.start(range)
      let end =  bf.end(range)
      if (range === 0) {
        // easy case, no user-seek
        let loadStartPercentage = start / node.duration;
        let loadEndPercentage = end / node.duration;
        loadPercentage = loadEndPercentage - loadStartPercentage;
      } else {
        let loaded = end - start
        let remainingToLoad = node.duration - start
        // user seeked a specific position in the audio, our progress must be
        // computed based on the remaining portion of the track
        loadPercentage = loaded / remainingToLoad;
      }
      this.$store.commit('player/bufferProgress', loadPercentage * 100)
    },
    updateProgress: function () {
      this.isUpdatingTime = true
      if (this.sound && this.sound.state() === 'loaded') {
        this.$store.dispatch('player/updateProgress', this.sound.seek())
        this.updateBuffer(this.sound._sounds[0]._node)
      }
    },
    observeProgress: function (enable) {
      let self = this
      if (enable) {
        if (self.progressInterval) {
          clearInterval(self.progressInterval)
        }
        self.progressInterval = setInterval(() => {
          self.updateProgress()
        }, 1000)
      } else {
        clearInterval(self.progressInterval)
      }
    },
    setCurrentTime (t) {
      if (t < 0 | t > this.duration) {
        return
      }
      if (t === this.sound.seek()) {
        return
      }
      if (t === 0) {
        this.updateProgressThrottled.cancel()
      }
      this.sound.seek(t)
    },
    ended: function () {
      let onlyTrack = this.$store.state.queue.tracks.length === 1
      if (this.looping === 1 || (onlyTrack && this.looping === 2)) {
        this.sound.seek(0)
        this.sound.play()
      } else {
        this.$store.dispatch('player/trackEnded', this.track)
      }
    }
  },
  watch: {
    playing: function (newValue) {
      if (newValue === true) {
        this.sound.play()
      } else {
        this.sound.pause()
      }
      this.observeProgress(newValue)
    },
    volume: function (newValue) {
      this.sound.volume(newValue)
    },
    currentTime (newValue) {
      if (!this.isUpdatingTime) {
        this.setCurrentTime(newValue)
      }
      this.isUpdatingTime = false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
