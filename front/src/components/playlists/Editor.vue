<template>
  <div class="ui text container">
    <h2 class="ui header">Playlist editor</h2>
    <p>Drag and drop rows to reorder tracks in the playlist</p>
    <div class="ui buttons">
      <div
        @click="insertMany(queueTracks)"
        :disabled="queueTracks.length === 0"
        :class="['ui', {disabled: queueTracks.length === 0}, 'button']"
        title="Copy tracks from current queue to playlist">Insert from queue ({{ queueTracks.length }} tracks)</div>
    </div>
    <h5 class="ui header">Status</h5>
    <div>
      <template v-if="status === 'loading'">
        <div class="ui active tiny inline loader"></div>
        Syncing changes to server...
      </template>
      <template v-else-if="status === 'errored'">
        <i class="red x icon"></i>
        An error occured while saving your changes
        <div v-if="errors.length > 0" class="ui negative message">
          <ul class="list">
            <li v-for="error in errors">{{ error }}</li>
          </ul>
        </div>
      </template>
      <template v-else-if="status === 'saved'">
        <i class="green check icon"></i> Changes synced with server
      </template>
    </div>
    <table class="ui compact very basic fixed single line unstackable table">
      <draggable v-model="plts" element="tbody" @update="reorder">
        <tr v-for="(plt, index) in plts" :key="plt.id">
          <td class="left aligned">{{ plt.index + 1}}</td>
          <td class="center aligned">
            <img class="ui mini image" v-if="plt.track.album.cover" :src="plt.track.album.cover">
            <img class="ui mini image" v-else src="../../assets/audio/default-cover.png">
          </td>
          <td colspan="4">
            <strong>{{ plt.track.title }}</strong><br />
              {{ plt.track.artist.name }}
          </td>
          <td class="right aligned">
            <i @click.stop="removePlt(index)" class="circular red trash icon"></i>
          </td>
        </tr>
      </draggable>
    </table>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import axios from 'axios'

import draggable from 'vuedraggable'

export default {
  components: {
    draggable
  },
  props: ['playlist', 'playlistTracks'],
  data () {
    return {
      plts: this.playlistTracks,
      isLoading: false,
      errors: []
    }
  },
  methods: {
    success () {
      this.isLoading = false
      this.errors = []
    },
    errored (errors) {
      this.isLoading = false
      this.errors = errors
    },
    reorder ({oldIndex, newIndex}) {
      let self = this
      self.isLoading = true
      let plt = this.plts[newIndex]
      let url = 'playlist-tracks/' + plt.id + '/'
      axios.patch(url, {index: newIndex}).then((response) => {
        self.success()
      }, error => {
        self.errored(error.backendErrors)
      })
    },
    removePlt (index) {
      let plt = this.plts[index]
      this.plts.splice(index, 1)
      let self = this
      self.isLoading = true
      let url = 'playlist-tracks/' + plt.id + '/'
      axios.delete(url).then((response) => {
        self.success()
      }, error => {
        self.errored(error.backendErrors)
      })
    },
    insertMany (tracks) {
      let self = this
      let ids = tracks.map(t => {
        return t.id
      })
      self.isLoading = true
      let url = 'playlists/' + this.playlist.id + '/add/'
      axios.post(url, {tracks: ids}).then((response) => {
        response.data.results.forEach(r => {
          self.plts.push(r)
        })
        self.success()
      }, error => {
        self.errored(error.backendErrors)
      })
    }
  },
  computed: {
    ...mapState({
      queueTracks: state => state.queue.tracks
    }),
    status () {
      if (this.isLoading) {
        return 'loading'
      }
      if (this.errors.length > 0) {
        return 'errored'
      }
      return 'saved'
    }
  },
  watch: {
    plts: {
      handler (newValue) {
        newValue.forEach((e, i) => {
          e.index = i
        })
        this.$emit('tracks-updated', newValue)
      },
      deep: true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
