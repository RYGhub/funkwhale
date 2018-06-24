<template>
  <audio
    ref="audio"
    @error="errored"
    @loadeddata="loaded"
    @durationchange="updateDuration"
    @timeupdate="updateProgressThrottled"
    @ended="ended"
    preload>
    <source
      @error="sourceErrored"
      v-for="src in srcs"
      :src="src.url"
      :type="src.type">
  </audio>
</template>

<script>
import {mapState} from 'vuex'
import url from '@/utils/url'
import _ from 'lodash'
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
      realTrack: this.track,
      sourceErrors: 0,
      isUpdatingTime: false
    }
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
      let file = this.realTrack.files[0]
      if (!file) {
        this.$store.dispatch('player/trackErrored')
        return []
      }
      let sources = [
        {type: file.mimetype, url: this.$store.getters['instance/absoluteUrl'](file.path)}
      ]
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
    errored: function () {
      let self = this
      setTimeout(
        () => { self.$store.dispatch('player/trackErrored') }
      , 1000)
    },
    sourceErrored: function () {
      this.sourceErrors += 1
      if (this.sourceErrors >= this.srcs.length) {
        // all sources failed
        this.errored()
      }
    },
    updateDuration: function (e) {
      if (!this.$refs.audio) {
        return
      }
      this.$store.commit('player/duration', this.$refs.audio.duration)
    },
    loaded: function () {
      if (!this.$refs.audio) {
        return
      }
      this.$refs.audio.volume = this.volume
      this.$store.commit('player/resetErrorCount')
      if (this.isCurrent) {
        this.$store.commit('player/duration', this.$refs.audio.duration)
        if (this.startTime) {
          this.setCurrentTime(this.startTime)
        }
        if (this.autoplay) {
          this.$store.commit('player/playing', true)
          this.$refs.audio.play()
        }
      }
    },
    updateProgress: function () {
      this.isUpdatingTime = true
      if (this.$refs.audio) {
        this.$store.dispatch('player/updateProgress', this.$refs.audio.currentTime)
      }
    },
    ended: function () {
      let onlyTrack = this.$store.state.queue.tracks.length === 1
      if (this.looping === 1 || (onlyTrack && this.looping === 2)) {
        this.setCurrentTime(0)
        this.$refs.audio.play()
      } else {
        this.$store.dispatch('player/trackEnded', this.realTrack)
      }
    },
    setCurrentTime (t) {
      if (t < 0 | t > this.duration) {
        return
      }
      if (t === this.$refs.audio.currentTime) {
        return
      }
      if (t === 0) {
        this.updateProgressThrottled.cancel()
      }
      this.$refs.audio.currentTime = t
    }
  },
  watch: {
    track: _.debounce(function (newValue) {
      this.realTrack = newValue
      this.setCurrentTime(0)
      this.$refs.audio.load()
    }, 1000, {leading: true, trailing: true}),
    playing: function (newValue) {
      if (newValue === true) {
        this.$refs.audio.play()
      } else {
        this.$refs.audio.pause()
      }
    },
    '$store.state.queue.currentIndex' () {
      if (this.$store.state.player.playing) {
        this.$refs.audio.play()
      }
    },
    volume: function (newValue) {
      this.$refs.audio.volume = newValue
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
