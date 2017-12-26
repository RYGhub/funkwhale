<template>
  <div class="player">
    <audio-track
      ref="currentAudio"
      v-if="currentTrack"
      :key="(currentIndex, currentTrack.id)"
      :is-current="true"
      :start-time="$store.state.player.currentTime"
      :autoplay="$store.state.player.playing"
      :track="currentTrack">
    </audio-track>

    <div v-if="currentTrack" class="track-area ui items">
      <div class="ui inverted item">
        <div class="ui tiny image">
          <img v-if="currentTrack.album.cover" :src="Track.getCover(currentTrack)">
          <img v-else src="../../assets/audio/default-cover.png">
        </div>
        <div class="middle aligned content">
          <router-link class="small header discrete link track" :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}">
            {{ currentTrack.title }}
          </router-link>
          <div class="meta">
            <router-link class="artist" :to="{name: 'library.artists.detail', params: {id: currentTrack.artist.id }}">
              {{ currentTrack.artist.name }}
            </router-link> /
            <router-link class="album" :to="{name: 'library.albums.detail', params: {id: currentTrack.album.id }}">
              {{ currentTrack.album.title }}
            </router-link>
          </div>
          <div class="description">
            <track-favorite-icon :track="currentTrack"></track-favorite-icon>
          </div>
        </div>
      </div>
    </div>
    <div class="progress-area" v-if="currentTrack">
      <div class="ui grid">
        <div class="left floated four wide column">
          <p class="timer start" @click="updateProgress(0)">{{currentTimeFormatted}}</p>
        </div>

        <div class="right floated four wide column">
          <p class="timer total">{{durationFormatted}}</p>
        </div>
      </div>
      <div ref="progress" class="ui small orange inverted progress" @click="touchProgress">
        <div class="bar" :data-percent="progress" :style="{ 'width': progress + '%' }"></div>
      </div>
    </div>

    <div class="two wide column controls ui grid">
      <div
        @click="previous"
        title="Previous track"
        class="two wide column control"
        :disabled="!hasPrevious">
          <i :class="['ui', {'disabled': !hasPrevious}, 'step', 'backward', 'big', 'icon']" ></i>
      </div>
      <div
        v-if="!playing"
        @click="togglePlay"
        title="Play track"
        class="two wide column control">
          <i :class="['ui', 'play', {'disabled': !currentTrack}, 'big', 'icon']"></i>
      </div>
      <div
        v-else
        @click="togglePlay"
        title="Pause track"
        class="two wide column control">
          <i :class="['ui', 'pause', {'disabled': !currentTrack}, 'big', 'icon']"></i>
      </div>
      <div
        @click="next"
        title="Next track"
        class="two wide column control"
        :disabled="!hasNext">
          <i :class="['ui', {'disabled': !hasNext}, 'step', 'forward', 'big', 'icon']" ></i>
      </div>
      <div class="two wide column control volume-control">
        <i title="Unmute" @click="$store.commit('player/volume', 1)" v-if="volume === 0" class="volume off secondary icon"></i>
        <i title="Mute" @click="$store.commit('player/volume', 0)" v-else-if="volume < 0.5" class="volume down secondary icon"></i>
        <i title="Mute" @click="$store.commit('player/volume', 0)" v-else class="volume up secondary icon"></i>
        <input type="range" step="0.05" min="0" max="1" v-model="sliderVolume" />
      </div>
      <div class="two wide column control looping">
        <i
          title="Looping disabled. Click to switch to single-track looping."
          v-if="looping === 0"
          @click="$store.commit('player/looping', 1)"
          :disabled="!currentTrack"
          :class="['ui', {'disabled': !currentTrack}, 'step', 'repeat', 'secondary', 'icon']"></i>
        <i
          title="Looping on a single track. Click to switch to whole queue looping."
          v-if="looping === 1"
          @click="$store.commit('player/looping', 2)"
          :disabled="!currentTrack"
          class="repeat secondary icon">
          <span class="ui circular tiny orange label">1</span>
        </i>
        <i
          title="Looping on whole queue. Click to disable looping."
          v-if="looping === 2"
          @click="$store.commit('player/looping', 0)"
          :disabled="!currentTrack"
          class="repeat orange secondary icon">
        </i>
      </div>
      <div
        @click="shuffle()"
        :disabled="queue.tracks.length === 0"
        title="Shuffle your queue"
        class="two wide column control">
        <i :class="['ui', 'random', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
      </div>
      <div class="one wide column"></div>
      <div
        @click="clean()"
        :disabled="queue.tracks.length === 0"
        title="Clear your queue"
        class="two wide column control">
        <i :class="['ui', 'trash', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
      </div>
    </div>
    <GlobalEvents
      @keydown.space.prevent.exact="togglePlay"
      @keydown.ctrl.left.prevent.exact="previous"
      @keydown.ctrl.right.prevent.exact="next"
      @keydown.ctrl.down.prevent.exact="$store.commit('player/incrementVolume', -0.1)"
      @keydown.ctrl.up.prevent.exact="$store.commit('player/incrementVolume', 0.1)"
      @keydown.f.prevent.exact="$store.dispatch('favorites/toggle', currentTrack.id)"
      @keydown.l.prevent.exact="$store.commit('player/toggleLooping')"
      @keydown.s.prevent.exact="shuffle"
      />

  </div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex'
import GlobalEvents from '@/components/utils/global-events'

import Track from '@/audio/track'
import AudioTrack from '@/components/audio/Track'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'

export default {
  name: 'player',
  components: {
    TrackFavoriteIcon,
    GlobalEvents,
    AudioTrack
  },
  data () {
    return {
      sliderVolume: this.volume,
      Track: Track
    }
  },
  mounted () {
    // we trigger the watcher explicitely it does not work otherwise
    this.sliderVolume = this.volume
  },
  methods: {
    ...mapActions({
      pause: 'player/pause',
      togglePlay: 'player/togglePlay',
      clean: 'queue/clean',
      next: 'queue/next',
      previous: 'queue/previous',
      shuffle: 'queue/shuffle',
      updateProgress: 'player/updateProgress'
    }),
    touchProgress (e) {
      let time
      let target = this.$refs.progress
      time = e.layerX / target.offsetWidth * this.duration
      this.$refs.currentAudio.setCurrentTime(time)
    }
  },
  computed: {
    ...mapState({
      currentIndex: state => state.queue.currentIndex,
      playing: state => state.player.playing,
      volume: state => state.player.volume,
      looping: state => state.player.looping,
      duration: state => state.player.duration,
      queue: state => state.queue
    }),
    ...mapGetters({
      currentTrack: 'queue/currentTrack',
      hasNext: 'queue/hasNext',
      hasPrevious: 'queue/hasPrevious',
      durationFormatted: 'player/durationFormatted',
      currentTimeFormatted: 'player/currentTimeFormatted',
      progress: 'player/progress'
    })
  },
  watch: {
    volume (newValue) {
      this.sliderVolume = newValue
    },
    sliderVolume (newValue) {
      this.$store.commit('player/volume', newValue)
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
