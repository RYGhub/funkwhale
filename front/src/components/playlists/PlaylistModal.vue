<template>
  <modal @update:show="update" :show="$store.state.playlists.showModal">
    <template v-if="track">
      <div class="header">
        Add "{{ track.title }}" by {{ track.artist.name }} to one of your playlists
      </div>
      <div class="scrolling content">
        <div class="description">
          <playlist-form></playlist-form>
          <div class="ui divider"></div>
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">We cannot add the track to a playlist</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <h4 class="ui header">Available playlists</h4>
          <table class="ui single line unstackable very basic table">
            <thead>
              <tr>
                <th>Name</th>
                <th class="sorted descending">Last modification</th>
                <th>Tracks</th>
                <th>Visibility</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="playlist in sortedPlaylists">
                <td><router-link :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">{{ playlist.name }}</router-link></td>
                <td><human-date :date="playlist.modification_date"></human-date></td>
                <td>{{ playlist.tracks_count }}</td>
                <td>{{ playlist.privacy_level }}</td>
                <td>
                  <div
                    class="ui green icon right floated button"
                    title="Add to this playlist"
                    @click="addToPlaylist(playlist.id)">
                  <i class="plus icon"></i>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="actions">
        <div class="ui cancel button">Cancel</div>
      </div>
    </template>
  </modal>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import {mapState} from 'vuex'

import logger from '@/logging'
import Modal from '@/components/semantic/Modal'
import PlaylistForm from '@/components/playlists/Form'

export default {
  components: {
    Modal,
    PlaylistForm
  },
  data () {
    return {
      errors: []
    }
  },
  methods: {
    update (v) {
      this.$store.commit('playlists/showModal', v)
    },
    addToPlaylist (playlistId) {
      let self = this
      let payload = {
        track: this.track.id,
        playlist: playlistId
      }
      return axios.post('playlist-tracks/', payload).then(response => {
        logger.default.info('Successfully added track to playlist')
        self.update(false)
        self.$store.dispatch('playlists/fetchOwn')
      }, error => {
        logger.default.error('Error while adding track to playlist')
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    ...mapState({
      playlists: state => state.playlists.playlists,
      track: state => state.playlists.modalTrack
    }),
    sortedPlaylists () {
      let p = _.sortBy(this.playlists, [(e) => { return e.modification_date }])
      p.reverse()
      return p
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
