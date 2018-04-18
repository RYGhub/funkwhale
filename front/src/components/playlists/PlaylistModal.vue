<template>
  <modal @update:show="update" :show="$store.state.playlists.showModal">
    <div class="header">
      {{ $t('Manage playlists') }}
    </div>
    <div class="scrolling content">
      <div class="description">
        <template v-if="track">
          <h4 class="ui header">{{ $t('Current track') }}</h4>
          <div>
            {{ $t('"{%title%}" by {%artist%}', { title: track.title, artist: track.artist.name }) }}
          </div>
          <div class="ui divider"></div>
        </template>

        <playlist-form></playlist-form>
        <div class="ui divider"></div>
        <div v-if="errors.length > 0" class="ui negative message">
          <div class="header">{{ $t('We cannot add the track to a playlist') }}</div>
          <ul class="list">
            <li v-for="error in errors">{{ error }}</li>
          </ul>
        </div>
        </div>
        <h4 class="ui header">{{ $t('Available playlists') }}</h4>
        <table class="ui unstackable very basic table">
          <thead>
            <tr>
              <th></th>
              <th>{{ $t('Name') }}</th>
              <th class="sorted descending">{{ $t('Last modification') }}</th>
              <th>{{ $t('Tracks') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="playlist in sortedPlaylists">
              <td>
                <router-link
                  class="ui icon basic small button"
                  :to="{name: 'library.playlists.detail', params: {id: playlist.id }, query: {mode: 'edit'}}"><i class="ui pencil icon"></i></router-link>
              </td>
              <td>
                <router-link :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">{{ playlist.name }}</router-link></td>
              <td><human-date :date="playlist.modification_date"></human-date></td>
              <td>{{ playlist.tracks_count }}</td>
              <td>
                <div
                  v-if="track"
                  class="ui green icon basic small right floated button"
                  :title="{{ $t('Add to this playlist') }}"
                  @click="addToPlaylist(playlist.id)">
                  <i class="plus icon"></i> {{ $t('Add track') }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="actions">
      <div class="ui cancel button">{{ $t('Cancel') }}</div>
    </div>
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
  },
  watch: {
    '$store.state.route.path' () {
      this.$store.commit('playlists/showModal', false)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
