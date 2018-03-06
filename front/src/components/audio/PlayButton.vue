<template>
  <div :class="['ui', {'tiny': discrete}, 'buttons']">
    <button
      title="Add to current queue"
      @click="add"
      :class="['ui', {loading: isLoading}, {'mini': discrete}, {disabled: playableTracks.length === 0}, 'button']">
      <i class="ui play icon"></i>
      <template v-if="!discrete"><slot>Play</slot></template>
    </button>
    <div v-if="!discrete" class="ui floating dropdown icon button">
      <i class="dropdown icon"></i>
      <div class="menu">
        <div class="item"@click="add"><i class="plus icon"></i> Add to queue</div>
        <div class="item"@click="addNext()"><i class="step forward icon"></i> Play next</div>
        <div class="item"@click="addNext(true)"><i class="arrow down icon"></i> Play now</div>
      </div>
    </div>
  </div>
</template>

<script>
import logger from '@/logging'
import jQuery from 'jquery'

export default {
  props: {
    // we can either have a single or multiple tracks to play when clicked
    tracks: {type: Array, required: false},
    track: {type: Object, required: false},
    discrete: {type: Boolean, default: false}
  },
  data () {
    return {
      isLoading: false
    }
  },
  created () {
    if (!this.track & !this.tracks) {
      logger.default.error('You have to provide either a track or tracks property')
    }
  },
  mounted () {
    if (!this.discrete) {
      jQuery(this.$el).find('.ui.dropdown').dropdown()
    }
  },
  computed: {
    playableTracks () {
      let tracks
      if (this.track) {
        tracks = [this.track]
      } else {
        tracks = this.tracks
      }
      return tracks.filter(e => {
        return e.files.length > 0
      })
    }
  },
  methods: {
    triggerLoad () {
      let self = this
      this.isLoading = true
      setTimeout(() => {
        self.isLoading = false
      }, 500)
    },
    add () {
      this.triggerLoad()
      this.$store.dispatch('queue/appendMany', {tracks: this.playableTracks})
    },
    addNext (next) {
      this.triggerLoad()
      this.$store.dispatch('queue/appendMany', {tracks: this.playableTracks, index: this.$store.state.queue.currentIndex + 1})
      if (next) {
        this.$store.dispatch('queue/next')
      }
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
