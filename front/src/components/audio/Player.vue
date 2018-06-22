<template>
  <div class="ui inverted segment player-wrapper" :style="style">
    <div class="player">
      <keep-alive>
        <audio-track
          ref="currentAudio"
          v-if="renderAudio && currentTrack"
          :is-current="true"
          :start-time="$store.state.player.currentTime"
          :autoplay="$store.state.player.playing"
          :track="currentTrack">
        </audio-track>
      </keep-alive>
      <div v-if="currentTrack" class="track-area ui unstackable items">
        <div class="ui inverted item">
          <div class="ui tiny image">
            <img ref="cover" @load="updateBackground" v-if="currentTrack.album.cover" :src="$store.getters['instance/absoluteUrl'](currentTrack.album.cover)">
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
              <track-favorite-icon
                v-if="$store.state.auth.authenticated"
                :track="currentTrack"></track-favorite-icon>
              <track-playlist-icon
                v-if="$store.state.auth.authenticated"
                :track="currentTrack"></track-playlist-icon>
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
          :title="$t('Previous track')"
          class="two wide column control"
          :disabled="emptyQueue">
            <i @click="previous" :class="['ui', 'backward', {'disabled': emptyQueue}, 'big', 'icon']"></i>
        </div>
        <div
          v-if="!playing"
          :title="$t('Play track')"
          class="two wide column control">
            <i @click="togglePlay" :class="['ui', 'play', {'disabled': !currentTrack}, 'big', 'icon']"></i>
        </div>
        <div
          v-else
          :title="$t('Pause track')"
          class="two wide column control">
            <i @click="togglePlay" :class="['ui', 'pause', {'disabled': !currentTrack}, 'big', 'icon']"></i>
        </div>
        <div
          :title="$t('Next track')"
          class="two wide column control"
          :disabled="!hasNext">
            <i @click="next" :class="['ui', {'disabled': !hasNext}, 'step', 'forward', 'big', 'icon']" ></i>
        </div>
        <div class="two wide column control volume-control">
          <i :title="$t('Unmute')" @click="$store.commit('player/volume', 1)" v-if="volume === 0" class="volume off secondary icon"></i>
          <i :title="$t('Mute')" @click="$store.commit('player/volume', 0)" v-else-if="volume < 0.5" class="volume down secondary icon"></i>
          <i :title="$t('Mute')" @click="$store.commit('player/volume', 0)" v-else class="volume up secondary icon"></i>
          <input type="range" step="0.05" min="0" max="1" v-model="sliderVolume" />
        </div>
        <div class="two wide column control looping">
          <i
            :title="$t('Looping disabled. Click to switch to single-track looping.')"
            v-if="looping === 0"
            @click="$store.commit('player/looping', 1)"
            :disabled="!currentTrack"
            :class="['ui', {'disabled': !currentTrack}, 'step', 'repeat', 'secondary', 'icon']"></i>
          <i
            :title="$t('Looping on a single track. Click to switch to whole queue looping.')"
            v-if="looping === 1"
            @click="$store.commit('player/looping', 2)"
            :disabled="!currentTrack"
            class="repeat secondary icon">
            <span class="ui circular tiny orange label">1</span>
          </i>
          <i
            :title="$t('Looping on whole queue. Click to disable looping.')"
            v-if="looping === 2"
            @click="$store.commit('player/looping', 0)"
            :disabled="!currentTrack"
            class="repeat orange secondary icon">
          </i>
        </div>
        <div
          :disabled="queue.tracks.length === 0"
          :title="$t('Shuffle your queue')"
          class="two wide column control">
          <div v-if="isShuffling" class="ui inline shuffling inverted small active loader"></div>
          <i v-else @click="shuffle()" :class="['ui', 'random', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
        </div>
        <div class="one wide column"></div>
        <div
          :disabled="queue.tracks.length === 0"
          :title="$t('Clear your queue')"
          class="two wide column control">
          <i @click="clean()" :class="['ui', 'trash', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
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
  </div>
</template>

<script>
import {mapState, mapGetters, mapActions} from 'vuex'
import GlobalEvents from '@/components/utils/global-events'
import ColorThief from '@/vendor/color-thief'

import AudioTrack from '@/components/audio/Track'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import TrackPlaylistIcon from '@/components/playlists/TrackPlaylistIcon'

export default {
  name: 'player',
  components: {
    TrackFavoriteIcon,
    TrackPlaylistIcon,
    GlobalEvents,
    AudioTrack
  },
  data () {
    let defaultAmbiantColors = [[46, 46, 46], [46, 46, 46], [46, 46, 46], [46, 46, 46]]
    return {
      isShuffling: false,
      renderAudio: true,
      sliderVolume: this.volume,
      defaultAmbiantColors: defaultAmbiantColors,
      ambiantColors: defaultAmbiantColors
    }
  },
  mounted () {
    // we trigger the watcher explicitely it does not work otherwise
    this.sliderVolume = this.volume
  },
  methods: {
    ...mapActions({
      togglePlay: 'player/togglePlay',
      clean: 'queue/clean',
      updateProgress: 'player/updateProgress'
    }),
    shuffle () {
      if (this.isShuffling) {
        return
      }
      let self = this
      this.isShuffling = true
      setTimeout(() => {
        self.$store.dispatch('queue/shuffle', () => {
          self.isShuffling = false
          self.$store.commit('ui/addMessage', {
            content: self.$t('Queue shuffled!'),
            date: new Date()
          })
        })
      }, 100)
    },
    next () {
      let self = this
      this.$store.dispatch('queue/next').then(() => {
        self.$emit('next')
      })
    },
    previous () {
      let self = this
      this.$store.dispatch('queue/previous').then(() => {
        self.$emit('previous')
      })
    },
    touchProgress (e) {
      let time
      let target = this.$refs.progress
      time = e.layerX / target.offsetWidth * this.duration
      this.$refs.currentAudio.setCurrentTime(time)
    },
    updateBackground () {
      if (!this.currentTrack.album.cover) {
        this.ambiantColors = this.defaultAmbiantColors
        return
      }
      let image = this.$refs.cover
      this.ambiantColors = ColorThief.prototype.getPalette(image, 4).slice(0, 4)
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
      emptyQueue: 'queue/isEmpty',
      durationFormatted: 'player/durationFormatted',
      currentTimeFormatted: 'player/currentTimeFormatted',
      progress: 'player/progress'
    }),
    style: function () {
      let style = {
        'background': this.ambiantGradiant
      }
      return style
    },
    ambiantGradiant: function () {
      let indexConf = [
        {orientation: 330, percent: 100, opacity: 0.7},
        {orientation: 240, percent: 90, opacity: 0.7},
        {orientation: 150, percent: 80, opacity: 0.7},
        {orientation: 60, percent: 70, opacity: 0.7}
      ]
      let gradients = this.ambiantColors.map((e, i) => {
        let [r, g, b] = e
        let conf = indexConf[i]
        return `linear-gradient(${conf.orientation}deg, rgba(${r}, ${g}, ${b}, ${conf.opacity}) 10%, rgba(255, 255, 255, 0) ${conf.percent}%)`
      }).join(', ')
      return gradients
    }
  },
  watch: {
    currentTrack (newValue) {
      if (!newValue || !newValue.album.cover) {
        this.ambiantColors = this.defaultAmbiantColors
      }
    },
    currentIndex (newValue, oldValue) {
      if (newValue !== oldValue) {
        // why this? to ensure the audio tag is deleted and fully
        // rerendered, so we don't have any issues with cached position
        // or whatever
        this.renderAudio = false
        this.$nextTick(() => {
          this.renderAudio = true
        })
      }
    },
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
  margin-top: 0;
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
  input[type=range] {
    -webkit-appearance: none;
  }
  input[type=range]:focus {
    outline: none;
  }
  input[type=range]::-webkit-slider-runnable-track {
    cursor: pointer;
    background: white;
  }
  input[type=range]::-webkit-slider-thumb {
    background: white;
    cursor: pointer;
    -webkit-appearance: none;
  }
  input[type=range]:focus::-webkit-slider-runnable-track {
    background: #white;
  }
  input[type=range]::-moz-range-track {
    cursor: pointer;
    background: white;
  }
  input[type=range]::-moz-range-thumb {
    background: white;
    cursor: pointer;
  }
  input[type=range]::-ms-track {
    cursor: pointer;
    background: transparent;
    border-color: transparent;
    color: transparent;
  }
  input[type=range]::-ms-fill-lower {
    background: white;
  }
  input[type=range]::-ms-fill-upper {
    background: white;
  }
  input[type=range]::-ms-thumb {
    background: white;
    cursor: pointer;
  }
  input[type=range]:focus::-ms-fill-lower {
    background: white;
  }
  input[type=range]:focus::-ms-fill-upper {
    background: #white;
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
.shuffling.loader.inline {
  margin: 0;
}

</style>
