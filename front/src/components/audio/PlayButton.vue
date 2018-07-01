<template>
  <div :title="title" :class="['ui', {'tiny': discrete}, 'buttons']">
    <button
      :title="$gettext('Add to current queue')"
      @click="addNext(true)"
      :disabled="!playable"
      :class="['ui', {loading: isLoading}, {'mini': discrete}, {disabled: !playable}, 'button']">
      <i class="ui play icon"></i>
      <template v-if="!discrete"><slot><translate>Play</translate></slot></template>
    </button>
    <div v-if="!discrete" :class="['ui', {disabled: !playable}, 'floating', 'dropdown', 'icon', 'button']">
      <i class="dropdown icon"></i>
      <div class="menu">
        <div class="item" :disabled="!playable" @click="add"><i class="plus icon"></i><translate>Add to queue</translate></div>
        <div class="item" :disabled="!playable" @click="addNext()"><i class="step forward icon"></i><translate>Play next</translate></div>
        <div class="item" :disabled="!playable" @click="addNext(true)"><i class="arrow down icon"></i><translate>Play now</translate></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import jQuery from 'jquery'

export default {
  props: {
    // we can either have a single or multiple tracks to play when clicked
    tracks: {type: Array, required: false},
    track: {type: Object, required: false},
    playlist: {type: Object, required: false},
    discrete: {type: Boolean, default: false},
    artist: {type: Number, required: false},
    album: {type: Number, required: false}
  },
  data () {
    return {
      isLoading: false
    }
  },
  mounted () {
    jQuery(this.$el).find('.ui.dropdown').dropdown()
  },
  computed: {
    title () {
      if (this.playable) {
        return this.$gettext('Play immediatly')
      } else {
        if (this.track) {
          return this.$gettext('This track is not imported and cannot be played')
        }
      }
    },
    playable () {
      if (this.track) {
        return this.track.files.length > 0
      } else if (this.tracks) {
        return this.tracks.length > 0
      } else if (this.playlist) {
        return true
      } else if (this.artist) {
        return true
      } else if (this.album) {
        return true
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
          return e.files.length > 0
        })
      })
    },
    add () {
      let self = this
      this.getPlayableTracks().then((tracks) => {
        self.$store.dispatch('queue/appendMany', {tracks: tracks}).then(() => self.addMessage(tracks))
      })
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
    },
    addMessage (tracks) {
      if (tracks.length < 1) {
        return
      }
      let msg = this.$ngettext('%{ count } track was added to your queue', '%{ count } tracks were added to your queue', tracks.length)
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
</style>
