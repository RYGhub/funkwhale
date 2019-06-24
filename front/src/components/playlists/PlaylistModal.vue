<template>
  <modal @update:show="update" :show="$store.state.playlists.showModal">
    <div class="header">
      <translate translate-context="Popup/Playlist/Title/Verb">Manage playlists</translate>
    </div>
    <div class="scrolling content">
      <div class="description">
        <template v-if="track">
          <h4 class="ui header"><translate translate-context="Popup/Playlist/Title">Current track</translate></h4>
          <span
            translate-context="Popup/Playlist/Paragraph"
            v-translate="{artist: track.artist.name, title: track.title}"
            :translate-params="{artist: track.artist.name, title: track.title}">
            "%{ title }", by %{ artist }
          </span>
          <div class="ui divider"></div>
        </template>

        <playlist-form :key="formKey"></playlist-form>
        <div class="ui divider"></div>
        <div v-if="showDuplicateTrackAddConfirmation" class="ui warning message">
          <p translate-context="Popup/Playlist/Paragraph"
            v-translate="{track: track.title, playlist: duplicateTrackAddInfo.playlist_name}"
            :translate-params="{track: track.title, playlist: duplicateTrackAddInfo.playlist_name}"><strong>%{ track }</strong> is already in <strong>%{ playlist }</strong>.</p>
          <button
            @click="update(false)"
            class="ui small cancel button"><translate translate-context="*/*/Button.Label/Verb">Cancel</translate>
          </button>
          <button
            class="ui small green button"
            @click="addToPlaylist(lastSelectedPlaylist, true)">
              <translate translate-context="*/Playlist/Button.Label/Verb">Add anyways</translate></button>
        </div>
        <div v-if="errors.length > 0" class="ui negative message">
          <div class="header"><translate translate-context="Popup/Playlist/Error message.Title">The track can't be added to a playlist</translate></div>
          <ul class="list">
            <li v-for="error in errors">{{ error }}</li>
          </ul>
        </div>
        </div>
        <h4 class="ui header"><translate translate-context="Popup/Playlist/Title">Available playlists</translate></h4>
        <table class="ui unstackable very basic table">
          <thead>
            <tr>
              <th></th>
              <th><translate translate-context="*/*/*/Noun">Name</translate></th>
              <th class="sorted descending"><translate translate-context="Popup/Playlist/Table.Label/Short">Last modification</translate></th>
              <th><translate translate-context="*/*/*/Noun">Tracks</translate></th>
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
              <td :title="playlist.name">
                <router-link v-on:click.native="update(false)" :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">{{ playlist.name }}</router-link></td>
              <td><human-date :date="playlist.modification_date"></human-date></td>
              <td>{{ playlist.tracks_count }}</td>
              <td>
                <div
                  v-if="track"
                  class="ui green icon basic small right floated button"
                  :title="labels.addToPlaylist"
                  @click="addToPlaylist(playlist.id, false)">
                  <i class="plus icon"></i> <translate translate-context="Popup/Playlist/Table.Button.Label/Verb">Add track</translate>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="actions">
      <div class="ui cancel button"><translate translate-context="*/*/Button.Label/Verb">Cancel</translate></div>
    </div>
  </modal>
</template>

<script>
import _ from '@/lodash'
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
      formKey: String(new Date()),
      errors: [],
      duplicateTrackAddInfo: {},
      showDuplicateTrackAddConfirmation: false,
      lastSelectedPlaylist: -1,
    }
  },
  methods: {
    update (v) {
      this.$store.commit('playlists/showModal', v)
    },
    addToPlaylist (playlistId, allowDuplicate) {
      let self = this
      let payload = {
        track: this.track.id,
        playlist: playlistId,
        allow_duplicates: allowDuplicate
      }

      self.lastSelectedPlaylist = playlistId

      return axios.post('playlist-tracks/', payload).then(response => {
        logger.default.info('Successfully added track to playlist')
        self.update(false)
        self.$store.dispatch('playlists/fetchOwn')
      }, error => {
        if (error.backendErrors.length == 1 && error.backendErrors[0].code == 'tracks_already_exist_in_playlist') {
          self.duplicateTrackAddInfo = error.backendErrors[0]
          self.showDuplicateTrackAddConfirmation = true
        } else {
          self.errors = error.backendErrors
          self.showDuplicateTrackAddConfirmation = false
        }
      })
    }
  },
  computed: {
    ...mapState({
      playlists: state => state.playlists.playlists,
      track: state => state.playlists.modalTrack
    }),
    labels () {
      return {
        addToPlaylist: this.$pgettext('Popup/Playlist/Table.Button.Tooltip/Verb', 'Add to this playlist')
      }
    },
    sortedPlaylists () {
      let p = _.sortBy(this.playlists, [(e) => { return e.modification_date }])
      p.reverse()
      return p
    }
  },
  watch: {
    '$store.state.route.path' () {
      this.$store.commit('playlists/showModal', false)
      this.showDuplicateTrackAddConfirmation = false
    },
    '$store.state.playlists.showModal' () {
      this.formKey = String(new Date())
      this.showDuplicateTrackAddConfirmation = false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
