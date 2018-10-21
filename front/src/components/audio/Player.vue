<template>
  <div class="ui inverted segment player-wrapper" :style="style">
    <div class="player">
      <audio-track
        ref="currentAudio"
        v-if="currentTrack"
        :is-current="true"
        :start-time="$store.state.player.currentTime"
        :autoplay="$store.state.player.playing"
        :key="audioKey"
        :track="currentTrack">
      </audio-track>
      <div v-if="currentTrack" class="track-area ui unstackable items">
        <div class="ui inverted item">
          <div class="ui tiny image">
            <img ref="cover" @load="updateBackground" v-if="currentTrack.album.cover && currentTrack.album.cover.original" :src="$store.getters['instance/absoluteUrl'](currentTrack.album.cover.medium_square_crop)">
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
                :class="{'inverted': !$store.getters['favorites/isFavorite'](currentTrack.id)}"
                :track="currentTrack"></track-favorite-icon>
              <track-playlist-icon
                v-if="$store.state.auth.authenticated"
                :class="['inverted']"
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
        <a
          href
          :title="labels.previousTrack"
          :aria-label="labels.previousTrack"
          class="two wide column control"
          @click.prevent.stop="previous"
          :disabled="emptyQueue">
            <i :class="['ui', 'backward', {'disabled': emptyQueue}, 'secondary', 'icon']"></i>
        </a>
        <a
          href
          v-if="!playing"
          :title="labels.play"
          :aria-label="labels.play"
          @click.prevent.stop="togglePlay"
          class="two wide column control">
            <i :class="['ui', 'play', {'disabled': !currentTrack}, 'secondary', 'icon']"></i>
        </a>
        <a
          href
          v-else
          :title="labels.pause"
          :aria-label="labels.pause"
          @click.prevent.stop="togglePlay"
          class="two wide column control">
            <i :class="['ui', 'pause', {'disabled': !currentTrack}, 'secondary', 'icon']"></i>
        </a>
        <a
          href
          :title="labels.next"
          :aria-label="labels.next"
          class="two wide column control"
          @click.prevent.stop="next"
          :disabled="!hasNext">
            <i :class="['ui', {'disabled': !hasNext}, 'step', 'forward', 'secondary', 'icon']" ></i>
        </a>
        <div
          class="wide column control volume-control"
          v-on:mouseover="showVolume = true"
          v-on:mouseleave="showVolume = false"
          v-bind:class="{ active : showVolume }">
          <a
            href
            v-if="volume === 0"
            :title="labels.unmute"
            :aria-label="labels.unmute"
            @click.prevent.stop="unmute">
            <i class="volume off secondary icon"></i>
          </a>
          <a
            href
            v-else-if="volume < 0.5"
            :title="labels.mute"
            :aria-label="labels.mute"
            @click.prevent.stop="mute">
            <i class="volume down secondary icon"></i>
          </a>
          <a
            href
            v-else
            :title="labels.mute"
            :aria-label="labels.mute"
            @click.prevent.stop="mute">
            <i class="volume up secondary icon"></i>
          </a>
          <input
            type="range"
            step="0.05"
            min="0"
            max="1"
            v-model="sliderVolume"
            v-if="showVolume" />
        </div>
        <div class="two wide column control looping" v-if="!showVolume">
          <a
            href
            v-if="looping === 0"
            :title="labels.loopingDisabled"
            :aria-label="labels.loopingDisabled"
            @click.prevent.stop="$store.commit('player/looping', 1)"
            :disabled="!currentTrack">
            <i :class="['ui', {'disabled': !currentTrack}, 'step', 'repeat', 'secondary', 'icon']"></i>
          </a>
          <a
            href
            @click.prevent.stop="$store.commit('player/looping', 2)"
            :title="labels.loopingSingle"
            :aria-label="labels.loopingSingle"
            v-if="looping === 1"
            :disabled="!currentTrack">
            <i
              class="repeat secondary icon">
              <span class="ui circular tiny orange label">1</span>
            </i>
          </a>
          <a
            href
            :title="labels.loopingWhole"
            :aria-label="labels.loopingWhole"
            v-if="looping === 2"
            :disabled="!currentTrack"
            @click.prevent.stop="$store.commit('player/looping', 0)">
            <i
              class="repeat orange secondary icon">
            </i>
          </a>
        </div>
        <a
          href
          :disabled="queue.tracks.length === 0"
          :title="labels.shuffle"
          :aria-label="labels.shuffle"
          v-if="!showVolume"
          @click.prevent.stop="shuffle()"
          class="two wide column control">
          <div v-if="isShuffling" class="ui inline shuffling inverted tiny active loader"></div>
          <i v-else :class="['ui', 'random', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
        </a>
        <div class="one wide column" v-if="!showVolume"></div>
        <a
          href
          :disabled="queue.tracks.length === 0"
          :title="labels.clear"
          :aria-label="labels.clear"
          v-if="!showVolume"
          @click.prevent.stop="clean()"
          class="two wide column control">
          <i :class="['ui', 'trash', 'secondary', {'disabled': queue.tracks.length === 0}, 'icon']" ></i>
        </a>
      </div>
      <GlobalEvents
        @keydown.space.prevent.exact="togglePlay"
        @keydown.ctrl.left.prevent.exact="previous"
        @keydown.ctrl.right.prevent.exact="next"
        @keydown.ctrl.down.prevent.exact="$store.commit('player/incrementVolume', -0.1)"
        @keydown.ctrl.up.prevent.exact="$store.commit('player/incrementVolume', 0.1)"
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
import {Howl} from 'howler'

import AudioTrack from '@/components/audio/Track'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import TrackPlaylistIcon from '@/components/playlists/TrackPlaylistIcon'

export default {
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
      sliderVolume: this.volume,
      defaultAmbiantColors: defaultAmbiantColors,
      showVolume: false,
      ambiantColors: defaultAmbiantColors,
      audioKey: String(new Date()),
      dummyAudio: null
    }
  },
  mounted () {
    // we trigger the watcher explicitely it does not work otherwise
    this.sliderVolume = this.volume
    // this is needed to unlock audio playing under some browsers,
    // cf https://github.com/goldfire/howler.js#mobilechrome-playback
    // but we never actually load those audio files
    this.dummyAudio = new Howl({
      preload: false,
      autoplay: false,
      src: ['noop.webm', 'noop.mp3']
    })
  },
  destroyed () {
    this.dummyAudio.unload()
  },
  methods: {
    ...mapActions({
      togglePlay: 'player/togglePlay',
      mute: 'player/mute',
      unmute: 'player/unmute',
      clean: 'queue/clean',
      updateProgress: 'player/updateProgress'
    }),
    shuffle () {
      let disabled = this.queue.tracks.length === 0
      if (this.isShuffling || disabled) {
        return
      }
      let self = this
      let msg = this.$gettext('Queue shuffled!')
      this.isShuffling = true
      setTimeout(() => {
        self.$store.dispatch('queue/shuffle', () => {
          self.isShuffling = false
          self.$store.commit('ui/addMessage', {
            content: msg,
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
    labels () {
      let previousTrack = this.$gettext('Previous track')
      let play = this.$gettext('Play track')
      let pause = this.$gettext('Pause track')
      let next = this.$gettext('Next track')
      let unmute = this.$gettext('Unmute')
      let mute = this.$gettext('Mute')
      let loopingDisabled = this.$gettext('Looping disabled. Click to switch to single-track looping.')
      let loopingSingle = this.$gettext('Looping on a single track. Click to switch to whole queue looping.')
      let loopingWhole = this.$gettext('Looping on whole queue. Click to disable looping.')
      let shuffle = this.$gettext('Shuffle your queue')
      let clear = this.$gettext('Clear your queue')
      return {
        previousTrack,
        play,
        pause,
        next,
        unmute,
        mute,
        loopingDisabled,
        loopingSingle,
        loopingWhole,
        shuffle,
        clear
      }
    },
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
    currentTrack (newValue, oldValue) {
      if (!this.isShuffling && newValue != oldValue) {
        this.audioKey = String(new Date())
      }
      if (!newValue || !newValue.album.cover) {
        this.ambiantColors = this.defaultAmbiantColors
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
.controls a {
  color: white;
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
  width: 12.5% !important;
  [type="range"] {
    max-width: 70%;
    position: absolute;
    bottom: 1.1rem;
    left: 25%;
    cursor: pointer;
  }
  input[type=range]:focus {
    outline: none;
  }
  input[type=range]::-webkit-slider-runnable-track {
    cursor: pointer;
  }
  input[type=range]::-webkit-slider-thumb {
    background: white;
    cursor: pointer;
    -webkit-appearance: none;
    border-radius: 3px;
    width: 10px;
  }
  input[type=range]::-moz-range-track {
    cursor: pointer;
    background: white;
    opacity: 0.3;
  }
  input[type=range]::-moz-focus-outer {
    border: 0;
  }
  input[type=range]::-moz-range-thumb {
    background: white;
    cursor: pointer;
    border-radius: 3px;
    width: 10px;
  }
  input[type=range]::-ms-track {
    cursor: pointer;
    background: transparent;
    border-color: transparent;
    color: transparent;
  }
  input[type=range]::-ms-fill-lower {
    background: white;
    opacity: 0.3;
  }
  input[type=range]::-ms-fill-upper {
    background: white;
    opacity: 0.3;
  }
  input[type=range]::-ms-thumb {
    background: white;
    cursor: pointer;
    border-radius: 3px;
    width: 10px;
  }
  input[type=range]:focus::-ms-fill-lower {
    background: white;
  }
  input[type=range]:focus::-ms-fill-upper {
    background: white;
  }
}

.active.volume-control {
  width: 60% !important;
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
