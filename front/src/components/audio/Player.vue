<template>
  <div class="player">
    <div v-if="queue.currentTrack" class="track-area ui items">
      <div class="ui inverted item">
        <div class="ui tiny image">
          <img v-if="queue.currentTrack.album.cover" :src="Track.getCover(queue.currentTrack)">
          <img v-else src="../../assets/audio/default-cover.png">
        </div>
        <div class="middle aligned content">
          <router-link class="small header discrete link track" :to="{name: 'browse.track', params: {id: queue.currentTrack.id }}">
            {{ queue.currentTrack.title }}
          </router-link>
          <div class="meta">
            <router-link class="artist" :to="{name: 'browse.artist', params: {id: queue.currentTrack.artist.id }}">
              {{ queue.currentTrack.artist.name }}
            </router-link> /
            <router-link class="album" :to="{name: 'browse.album', params: {id: queue.currentTrack.album.id }}">
              {{ queue.currentTrack.album.title }}
            </router-link>
          </div>
          <div class="description">
            <track-favorite-icon :track="queue.currentTrack"></track-favorite-icon>
          </div>
        </div>
      </div>
    </div>
    <div class="progress-area">
      <div class="ui grid">
        <div class="left floated four wide column">
          <p class="timer start" @click="queue.audio.setTime(0)">{{queue.audio.state.currentTimeFormat}}</p>
        </div>

        <div class="right floated four wide column">
          <p class="timer total">{{queue.audio.state.durationTimerFormat}}</p>
        </div>
      </div>
      <div ref="progress" class="ui small orange inverted progress" @click="touchProgress">
        <div class="bar" :data-percent="queue.audio.state.progress" :style="{ 'width': queue.audio.state.progress + '%' }"></div>
      </div>
    </div>

    <div class="controls ui grid">
      <div class="volume-control four wide center aligned column">
        <input type="range" step="0.05" min="0" max="1" v-model="sliderVolume" />
        <i title="Unmute" @click="queue.setVolume(1)" v-if="currentVolume === 0" class="volume off secondary icon"></i>
        <i title="Mute" @click="queue.setVolume(0)" v-else-if="currentVolume < 0.5" class="volume down secondary icon"></i>
        <i title="Mute" @click="queue.setVolume(0)" v-else class="volume up secondary icon"></i>
      </div>
      <div class="eight wide center aligned column">
        <i title="Previous track" @click="queue.previous()" :class="['ui', {'disabled': !hasPrevious}, 'step', 'backward', 'big', 'icon']" :disabled="!hasPrevious"></i>
        <i title="Play track" v-if="!queue.audio.state.playing" :class="['ui', 'play', {'disabled': !queue.currentTrack}, 'big', 'icon']" @click="pauseOrPlay"></i>
        <i title="Pause track" v-else :class="['ui', 'pause', {'disabled': !queue.currentTrack}, 'big', 'icon']" @click="pauseOrPlay"></i>
        <i title="Next track" @click="queue.next()" :class="['ui', 'step', 'forward', {'disabled': !hasNext}, 'big', 'icon']" :disabled="!hasNext"></i>
      </div>
      <div class="four wide center aligned column">
        <i title="Clear your queue" @click="queue.clean()" :class="['ui', 'trash', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" :disabled="queue.tracks.length === 0"></i>
      </div>
    </div>
  </div>
</template>

<script>
import queue from '@/audio/queue'
import Track from '@/audio/track'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import radios from '@/radios'

export default {
  name: 'player',
  components: {
    TrackFavoriteIcon
  },
  data () {
    return {
      sliderVolume: this.currentVolume,
      queue: queue,
      Track: Track,
      radios
    }
  },
  mounted () {
    // we trigger the watcher explicitely it does not work otherwise
    this.sliderVolume = this.currentVolume
  },
  methods: {
    pauseOrPlay () {
      if (this.queue.audio.state.playing) {
        this.queue.audio.pause()
      } else {
        this.queue.audio.play()
      }
    },
    touchProgress (e) {
      let time
      let target = this.$refs.progress
      time = e.layerX / target.offsetWidth * this.queue.audio.state.duration
      this.queue.audio.setTime(time)
    }
  },
  computed: {
    hasPrevious () {
      return this.queue.currentIndex > 0
    },
    hasNext () {
      return this.queue.currentIndex < this.queue.tracks.length - 1
    },
    currentVolume () {
      return this.queue.audio.state.volume
    }
  },
  watch: {
    currentVolume (newValue) {
      this.sliderVolume = newValue
    },
    sliderVolume (newValue) {
      this.queue.setVolume(parseFloat(newValue))
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

.ui.progress {
  margin: 0.5rem 0 1rem;
}
.progress {
  cursor: pointer;
  .bar {
    min-width: 0 !important;
  }
}

.ui.inverted.item > .content > .description {
  color: rgba(255, 255, 255, 0.9) !important;
}

.ui.item {
  .meta {
    font-size: 90%;
    line-height: 1.2
  }
}
.timer.total {
    text-align: right;
}
.timer.start {
    cursor: pointer
}
.track-area {
  .header, .meta, .artist, .album {
    color: white !important;
  }
}

.controls .icon.big {
  cursor: pointer;
  font-size: 2em !important;
}

.controls .icon {
  cursor: pointer;
  vertical-align: middle;
}

.secondary.icon {
  font-size: 1.5em;
}
.progress-area .actions {
  text-align: center;
}
.volume-control {
  position: relative;
  .icon {
    margin: 0;
  }
  [type="range"] {
    max-width: 75%;
    position: absolute;
    bottom: 5px;
    left: 10%;
    cursor: pointer;
  }
}
.ui.feed.icon {
  margin: 0;
}
</style>
