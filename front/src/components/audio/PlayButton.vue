<template>
  <span :title="title" :class="['ui', {'tiny': discrete}, {'buttons': !dropdownOnly && !iconOnly}]">
    <button
      v-if="!dropdownOnly"
      :title="labels.playNow"
      @click="addNext(true)"
      :disabled="!playable"
      :class="buttonClasses.concat(['ui', {loading: isLoading}, {'mini': discrete}, {disabled: !playable}])">
      <i :class="[playIconClass, 'icon']"></i>
      <template v-if="!discrete && !iconOnly"><slot><translate :translate-context="'*/Queue/Button/Label/Short, Verb'">Play</translate></slot></template>
    </button>
    <div v-if="!discrete && !iconOnly" :class="['ui', {disabled: !playable}, 'floating', 'dropdown', {'icon': !dropdownOnly}, {'button': !dropdownOnly}]">
      <i :class="dropdownIconClasses.concat(['icon'])"></i>
      <div class="menu">
        <button class="item basic" ref="add" data-ref="add" :disabled="!playable" @click.stop.prevent="add" :title="labels.addToQueue">
          <i class="plus icon"></i><translate :translate-context="'*/Queue/Dropdown/Button/Label/Short'">Add to queue</translate>
        </button>
        <button class="item basic" ref="addNext" data-ref="addNext" :disabled="!playable" @click.stop.prevent="addNext()" :title="labels.playNext">
          <i class="step forward icon"></i><translate :translate-context="'*/Queue/Dropdown/Button/Label/Short'">Play next</translate>
        </button>
        <button class="item basic" ref="playNow" data-ref="playNow" :disabled="!playable" @click.stop.prevent="addNext(true)" :title="labels.playNow">
          <i class="play icon"></i><translate :translate-context="'*/Queue/Dropdown/Button/Label/Short'">Play now</translate>
        </button>
        <button v-if="track" class="item basic" :disabled="!playable" @click.stop.prevent="$store.dispatch('radios/start', {type: 'similar', objectId: track.id})" :title="labels.startRadio">
          <i class="feed icon"></i><translate :translate-context="'*/Queue/Dropdown/Button/Label/Short'">Start radio</translate>
        </button>
      </div>
    </div>
  </span>
</template>

<script>
import axios from 'axios'
import jQuery from 'jquery'

export default {
  props: {
    // we can either have a single or multiple tracks to play when clicked
    tracks: {type: Array, required: false},
    track: {type: Object, required: false},
    dropdownIconClasses: {type: Array, required: false, default: () => { return ['dropdown'] }},
    playIconClass: {type: String, required: false, default: 'play icon'},
    buttonClasses: {type: Array, required: false, default: () => { return ['button'] }},
    playlist: {type: Object, required: false},
    discrete: {type: Boolean, default: false},
    dropdownOnly: {type: Boolean, default: false},
    iconOnly: {type: Boolean, default: false},
    artist: {type: Number, required: false},
    album: {type: Number, required: false},
    isPlayable: {type: Boolean, required: false, default: null}
  },
  data () {
    return {
      isLoading: false
    }
  },
  mounted () {
    let self = this
    jQuery(this.$el).find('.ui.dropdown').dropdown({
      selectOnKeydown: false,
      action: function (text, value, $el) {
        // used ton ensure focusing the dropdown and clicking via keyboard
        // works as expected
        self.$refs[$el.data('ref')].click()
        jQuery(self.$el).find('.ui.dropdown').dropdown('hide')
      }
    })
  },
  computed: {
    labels () {
      return {
        playNow: this.$pgettext('*/Queue/Dropdown/Button/Title', 'Play now'),
        addToQueue: this.$pgettext('*/Queue/Dropdown/Button/Title', 'Add to current queue'),
        playNext: this.$pgettext('*/Queue/Dropdown/Button/Title', 'Play next'),
        startRadio: this.$pgettext('*/Queue/Dropdown/Button/Title', 'Play similar songs')
      }
    },
    title () {
      if (this.playable) {
        return this.$pgettext('*/Queue/Button/Title', 'Play...')
      } else {
        if (this.track) {
          return this.$pgettext('*/Queue/Button/Title', 'This track is not available in any library you have access to')
        }
      }
    },
    playable () {
      if (this.isPlayable) {
        return true
      }
      if (this.track) {
        return this.track.uploads && this.track.uploads.length > 0
      } else if (this.artist) {
        return this.albums.filter((a) => {
          return a.is_playable === true
        }).length > 0
      } else if (this.tracks) {
        return this.tracks.filter((t) => {
          return t.uploads && t.uploads.length > 0
        }).length > 0
      }
      return false
    }
  },
  methods: {
    getTracksPage (page, params, resolve, tracks) {
      if (page > 10) {
        // it's 10 * 100 tracks already, let's stop here
        resolve(tracks)
      }
      // when fetching artists/or album tracks, sometimes, we may have to fetch
      // multiple pages
      let self = this
      params['page_size'] = 100
      params['page'] = page
      tracks = tracks || []
      axios.get('tracks/', {params: params}).then((response) => {
        response.data.results.forEach(t => {
          tracks.push(t)
        })
        if (response.data.next) {
          self.getTracksPage(page + 1, params, resolve, tracks)
        } else {
          resolve(tracks)
        }
      })
    },
    getPlayableTracks () {
      let self = this
      this.isLoading = true
      let getTracks = new Promise((resolve, reject) => {
        if (self.track) {
          if (!self.track.uploads || self.track.uploads.length === 0) {
            // fetch uploads from api
            axios.get(`tracks/${self.track.id}/`).then((response) => {
              resolve([response.data])
            })
          } else {
            resolve([self.track])
          }
        } else if (self.tracks) {
          resolve(self.tracks)
        } else if (self.playlist) {
          let url = 'playlists/' + self.playlist.id + '/'
          axios.get(url + 'tracks/').then((response) => {
            resolve(response.data.results.map(plt => {
              return plt.track
            }))
          })
        } else if (self.artist) {
          let params = {'artist': self.artist, 'ordering': 'album__release_date,position'}
          self.getTracksPage(1, params, resolve)
        } else if (self.album) {
          let params = {'album': self.album, 'ordering': 'position'}
          self.getTracksPage(1, params, resolve)
        }
      })
      return getTracks.then((tracks) => {
        setTimeout(e => {
          self.isLoading = false
        }, 250)
        return tracks.filter(e => {
          return e.uploads && e.uploads.length > 0
        })
      })
    },
    add () {
      let self = this
      this.getPlayableTracks().then((tracks) => {
        self.$store.dispatch('queue/appendMany', {tracks: tracks}).then(() => self.addMessage(tracks))
      })
      jQuery(self.$el).find('.ui.dropdown').dropdown('hide')
    },
    addNext (next) {
      let self = this
      let wasEmpty = this.$store.state.queue.tracks.length === 0
      this.getPlayableTracks().then((tracks) => {
        self.$store.dispatch('queue/appendMany', {tracks: tracks, index: self.$store.state.queue.currentIndex + 1}).then(() => self.addMessage(tracks))
        let goNext = next && !wasEmpty
        if (goNext) {
          self.$store.dispatch('queue/next')
        }
      })
      jQuery(self.$el).find('.ui.dropdown').dropdown('hide')
    },
    addMessage (tracks) {
      if (tracks.length < 1) {
        return
      }
      let msg = this.$npgettext('*/Queue/Message', '%{ count } track was added to your queue', '%{ count } tracks were added to your queue', tracks.length)
      this.$store.commit('ui/addMessage', {
        content: this.$gettextInterpolate(msg, {count: tracks.length}),
        date: new Date()
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
button.item {
  background-color: white;
  width: 100%;
}
</style>
