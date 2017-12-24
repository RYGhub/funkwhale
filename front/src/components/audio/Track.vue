<template>
  <audio
    ref="audio"
    :src="url"
    @error="errored"
    @progress="updateLoad"
    @loadeddata="loaded"
    @timeupdate="updateProgress"
    @ended="ended"
    preload>

  </audio>
</template>

<script>
import {mapState} from 'vuex'
import backend from '@/audio/backend'
import url from '@/utils/url'

// import logger from '@/logging'

export default {
  props: {
    track: {type: Object},
    isCurrent: {type: Boolean, default: false}
  },
  computed: {
    ...mapState({
      playing: state => state.player.playing,
      currentTime: state => state.player.currentTime,
      duration: state => state.player.duration,
      volume: state => state.player.volume,
      looping: state => state.player.looping
    }),
    url: function () {
      let file = this.track.files[0]
      if (!file) {
        this.$store.dispatch('player/trackErrored')
        return null
      }
      let path = backend.absoluteUrl(file.path)
      if (this.$store.state.auth.authenticated) {
        // we need to send the token directly in url
        // so authentication can be checked by the backend
        // because for audio files we cannot use the regular Authentication
        // header
        path = url.updateQueryString(path, 'jwt', this.$store.state.auth.token)
      }
      return path
    }
  },
  methods: {
    errored: function () {
      this.$store.dispatch('player/trackErrored')
    },
    updateLoad: function () {

    },
    loaded: function () {
      this.$store.commit('player/duration', this.$refs.audio.duration)
      if (this.isCurrent) {
        this.$store.commit('player/playing', true)
        this.$refs.audio.play()
      }
    },
    updateProgress: function () {
      if (this.$refs.audio) {
        this.$store.dispatch('player/updateProgress', this.$refs.audio.currentTime)
      }
    },
    ended: function () {
      if (this.looping === 1) {
        this.setCurrentTime(0)
        this.$refs.audio.play()
      }
      this.$store.dispatch('player/trackEnded', this.track)
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
