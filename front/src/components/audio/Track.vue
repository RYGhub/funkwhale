<template>
  <audio
    ref="audio"
    @error="errored"
    @loadeddata="loaded"
    @durationchange="updateDuration"
    @timeupdate="updateProgress"
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
import formats from '@/audio/formats'
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
      sourceErrors: 0
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
      let file = this.track.files[0]
      if (!file) {
        this.$store.dispatch('player/trackErrored')
        return []
      }
      let sources = [
        {type: file.mimetype, url: file.path}
      ]
      formats.formats.forEach(f => {
        if (f !== file.mimetype) {
          let format = formats.formatsMap[f]
          let url = `/api/v1/trackfiles/transcode/?track_file=${file.id}&to=${format}`
          sources.push({type: f, url: url})
        }
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
    }
  },
  methods: {
    errored: function () {
      this.$store.dispatch('player/trackErrored')
    },
    sourceErrored: function () {
      this.sourceErrors += 1
      if (this.sourceErrors >= this.srcs.length) {
        // all sources failed
        this.errored()
      }
    },
    updateDuration: function (e) {
      this.$store.commit('player/duration', this.$refs.audio.duration)
    },
    loaded: function () {
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
    updateProgress: _.throttle(function () {
      if (this.$refs.audio) {
        this.$store.dispatch('player/updateProgress', this.$refs.audio.currentTime)
      }
    }, 250),
    ended: function () {
      let onlyTrack = this.$store.state.queue.tracks.length === 1
      if (this.looping === 1 || (onlyTrack && this.looping === 2)) {
        this.setCurrentTime(0)
        this.$refs.audio.play()
      } else {
        this.$store.dispatch('player/trackEnded', this.track)
      }
    },
    setCurrentTime (t) {
      if (t < 0 | t > this.duration) {
        return
      }
      this.updateProgress(t)
      this.$refs.audio.currentTime = t
    }
  },
  watch: {
    playing: function (newValue) {
      if (newValue === true) {
        this.$refs.audio.play()
      } else {
        this.$refs.audio.pause()
      }
    },
    volume: function (newValue) {
      this.$refs.audio.volume = newValue
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
