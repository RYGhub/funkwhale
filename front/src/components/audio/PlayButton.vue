<template>
  <div :class="['ui', {'tiny': discrete}, 'buttons']">
    <button
      :title="$t('Add to current queue')"
      @click="add"
      :class="['ui', {loading: isLoading}, {'mini': discrete}, {disabled: !playable}, 'button']">
      <i class="ui play icon"></i>
      <template v-if="!discrete"><slot><i18next path="Play"/></slot></template>
    </button>
    <div v-if="!discrete" :class="['ui', {disabled: !playable}, 'floating', 'dropdown', 'icon', 'button']">
      <i class="dropdown icon"></i>
      <div class="menu">
        <div class="item"@click="add"><i class="plus icon"></i><i18next path="Add to queue"/></div>
        <div class="item"@click="addNext()"><i class="step forward icon"></i><i18next path="Play next"/></div>
        <div class="item"@click="addNext(true)"><i class="arrow down icon"></i><i18next path="Play now"/></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'
import jQuery from 'jquery'

export default {
  props: {
    // we can either have a single or multiple tracks to play when clicked
    tracks: {type: Array, required: false},
    track: {type: Object, required: false},
    playlist: {type: Object, required: false},
    discrete: {type: Boolean, default: false}
  },
  data () {
    return {
      isLoading: false
    }
  },
  created () {
    if (!this.playlist && !this.track && !this.tracks) {
      logger.default.error('You have to provide either a track playlist or tracks property')
    }
  },
  mounted () {
    if (!this.discrete) {
      jQuery(this.$el).find('.ui.dropdown').dropdown()
    }
  },
  computed: {
    playable () {
      if (this.track) {
        return true
      } else if (this.tracks) {
        return this.tracks.length > 0
      } else if (this.playlist) {
        return true
      }
      return false
    }
  },
  methods: {
    getPlayableTracks () {
      let self = this
      let getTracks = new Promise((resolve, reject) => {
        if (self.track) {
          resolve([self.track])
        } else if (self.tracks) {
          resolve(self.tracks)
        } else if (self.playlist) {
          let url = 'playlists/' + self.playlist.id + '/'
          axios.get(url + 'tracks').then((response) => {
            resolve(response.data.results.map(plt => {
              return plt.track
            }))
          })
        }
      })
      return getTracks.then((tracks) => {
        return tracks.filter(e => {
          return e.files.length > 0
        })
      })
    },
    triggerLoad () {
      let self = this
      this.isLoading = true
      setTimeout(() => {
        self.isLoading = false
      }, 500)
    },
    add () {
      let self = this
      this.triggerLoad()
      this.getPlayableTracks().then((tracks) => {
        self.$store.dispatch('queue/appendMany', {tracks: tracks})
      })
    },
    addNext (next) {
      let self = this
      this.triggerLoad()
      this.getPlayableTracks().then((tracks) => {
        self.$store.dispatch('queue/appendMany', {tracks: tracks, index: self.$store.state.queue.currentIndex + 1})
        if (next) {
          self.$store.dispatch('queue/next')
        }
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
i {
  cursor: pointer;
}
</style>
