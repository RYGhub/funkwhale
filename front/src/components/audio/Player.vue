<template>
  <div class="player">
    <div v-if="queue.currentTrack" class="track-area ui items">
      <div class="ui inverted item">
        <div class="ui tiny image">
          <img v-if="queue.currentTrack.album.cover" :src="Track.getCover(queue.currentTrack)">
          <img v-else src="../../assets/audio/default-cover.png">
        </div>
        <div class="middle aligned content">
          <router-link class="small header discrete link track" :to="{name: 'library.tracks.detail', params: {id: queue.currentTrack.id }}">
            {{ queue.currentTrack.title }}
          </router-link>
          <div class="meta">
            <router-link class="artist" :to="{name: 'library.artists.detail', params: {id: queue.currentTrack.artist.id }}">
              {{ queue.currentTrack.artist.name }}
            </router-link> /
            <router-link class="album" :to="{name: 'library.albums.detail', params: {id: queue.currentTrack.album.id }}">
              {{ queue.currentTrack.album.title }}
            </router-link>
          </div>
          <div class="description">
            <track-favorite-icon :track="queue.currentTrack"></track-favorite-icon>
          </div>
        </div>
      </div>
    </div>
    <div class="progress-area" v-if="queue.currentTrack">
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

    <div class="two wide column controls ui grid">
      <div
        @click="queue.previous()"
        title="Previous track"
        class="two wide column control"
        :disabled="!hasPrevious">
          <i :class="['ui', {'disabled': !hasPrevious}, 'step', 'backward', 'big', 'icon']" ></i>
      </div>
      <div
        v-if="!queue.audio.state.playing"
        @click="pauseOrPlay"
        title="Play track"
        class="two wide column control">
          <i :class="['ui', 'play', {'disabled': !queue.currentTrack}, 'big', 'icon']"></i>
      </div>
      <div
        v-else
        @click="pauseOrPlay"
        title="Pause track"
        class="two wide column control">
          <i :class="['ui', 'pause', {'disabled': !queue.currentTrack}, 'big', 'icon']"></i>
      </div>
      <div
        @click="queue.next()"
        title="Next track"
        class="two wide column control"
        :disabled="!hasNext">
          <i :class="['ui', {'disabled': !hasPrevious}, 'step', 'forward', 'big', 'icon']" ></i>
      </div>
      <div class="two wide column control volume-control">
        <i title="Unmute" @click="queue.setVolume(1)" v-if="currentVolume === 0" class="volume off secondary icon"></i>
        <i title="Mute" @click="queue.setVolume(0)" v-else-if="currentVolume < 0.5" class="volume down secondary icon"></i>
        <i title="Mute" @click="queue.setVolume(0)" v-else class="volume up secondary icon"></i>
        <input type="range" step="0.05" min="0" max="1" v-model="sliderVolume" />
      </div>
      <div class="two wide column control looping">
        <i
          title="Looping disabled. Click to switch to single-track looping."
          v-if="queue.state.looping === 0"
          @click="queue.state.looping = 1"
          :disabled="!queue.currentTrack"
          :class="['ui', {'disabled': !queue.currentTrack}, 'step', 'repeat', 'secondary', 'icon']"></i>
        <i
          title="Looping on a single track. Click to switch to whole queue looping."
          v-if="queue.state.looping === 1"
          @click="queue.state.looping = 2"
          :disabled="!queue.currentTrack"
          class="repeat secondary icon">
          <span class="ui circular tiny orange label">1</span>
        </i>
        <i
          title="Looping on whole queue. Click to disable looping."
          v-if="queue.state.looping === 2"
          @click="queue.state.looping = 0"
          :disabled="!queue.currentTrack"
          class="repeat orange secondary icon">
        </i>
      </div>
      <div class="three wide column"></div>
      <div
        @click="queue.clean()"
        :disabled="queue.tracks.length === 0"
        title="Clear your queue"
        class="two wide column control">
        <i :class="['ui', 'trash', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
      </div>
    </div>
    <GlobalEvents
      @keydown.space.prevent.exact="pauseOrPlay"
      @keydown.ctrl.left.prevent.exact="queue.previous"
      @keydown.ctrl.right.prevent.exact="queue.next"
      @keydown.ctrl.down.prevent.exact="queue.incrementVolume(-0.1)"
      @keydown.ctrl.up.prevent.exact="queue.incrementVolume(0.1)"
      @keydown.f.prevent.exact="favoriteTracks.toggle(queue.currentTrack.id)"
      @keydown.l.prevent.exact="queue.toggleLooping"
      />

  </div>
</template>

<script>
import GlobalEvents from '@/components/utils/global-events'

import favoriteTracks from '@/favorites/tracks'
import queue from '@/audio/queue'
import radios from '@/radios'
import Track from '@/audio/track'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'

export default {
  name: 'player',
  components: {
    TrackFavoriteIcon,
    GlobalEvents
  },
  data () {
    return {
      sliderVolume: this.currentVolume,
      queue: queue,
      Track: Track,
      favoriteTracks,
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
    // margin: 0;
  }
  [type="range"] {
    max-width: 100%;
    position: absolute;
    bottom: 5px;
    left: 10%;
    cursor: pointer;
    display: none;
  }
  &:hover {
    [type="range"] {
      display: block;
    }
  }
}

.looping.control {
  i {
    position: relative;
  }
  .label {
    position: absolute;
    font-size: 0.7rem;
    bottom: -0.7rem;
    right: -0.7rem;
  }
}
.ui.feed.icon {
  margin: 0;
}
</style>
