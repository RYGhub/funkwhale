<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="labels.playlist">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="!isLoading && playlist" class="ui head vertical center aligned stripe segment" v-title="playlist.name">
      <div class="segment-content">
        <h2 class="ui center aligned icon header">
          <i class="circular inverted list yellow icon"></i>
          <div class="content">
            {{ playlist.name }}
            <div class="sub header">
              <translate
                translate-plural="Playlist containing %{ count } tracks, by %{ username }"
                :translate-n="playlistTracks.length"
                :translate-params="{count: playlistTracks.length, username: playlist.user.username}">
                Playlist containing %{ count } track, by %{ username }
              </translate><br>
              <duration :seconds="playlist.duration" />
            </div>
          </div>
        </h2>
        <div class="ui hidden divider"></div>
        <play-button class="orange" :tracks="tracks"><translate>Play all</translate></play-button>
        <button
          class="ui icon button"
          v-if="playlist.user.id === $store.state.auth.profile.id"
          @click="edit = !edit">
          <i class="pencil icon"></i>
          <template v-if="edit"><translate>End edition</translate></template>
          <template v-else><translate>Edit...</translate></template>
        </button>
        <dangerous-button v-if="playlist.user.id === $store.state.auth.profile.id" class="labeled icon" :action="deletePlaylist">
          <i class="trash icon"></i> <translate>Delete</translate>
          <p slot="modal-header">
            <translate :translate-params="{playlist: playlist.name}">Do you want to delete the playlist "%{ playlist }"?</translate>
          </p>
          <p slot="modal-content"><translate>This will completely delete this playlist and cannot be undone.</translate></p>
          <p slot="modal-confirm"><translate>Delete playlist</translate></p>
        </dangerous-button>
      </div>
    </div>
    <div class="ui vertical stripe segment">
      <template v-if="edit">
        <playlist-editor
          @playlist-updated="playlist = $event"
          @tracks-updated="updatePlts"
          :playlist="playlist" :playlist-tracks="playlistTracks"></playlist-editor>
      </template>
      <template v-else>
        <h2><translate>Tracks</translate></h2>
        <track-table :display-position="true" :tracks="tracks"></track-table>
      </template>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'
import PlayButton from '@/components/audio/PlayButton'
import PlaylistEditor from '@/components/playlists/Editor'

export default {
  props: {
    id: {required: true},
    defaultEdit: {type: Boolean, default: false}
  },
  components: {
    PlaylistEditor,
    TrackTable,
    PlayButton,
    RadioButton
  },
  data: function () {
    return {
      edit: this.defaultEdit,
      isLoading: false,
      playlist: null,
      tracks: [],
      playlistTracks: []
    }
  },
  created: function () {
    this.fetch()
  },
  computed: {
    labels () {
      return {
        playlist: this.$gettext('Playlist')
      }
    }
  },
  methods: {
    updatePlts (v) {
      this.playlistTracks = v
      this.tracks = v.map((e, i) => {
        let track = e.track
        track.position = i + 1
        return track
      })
    },
    fetch: function () {
      let self = this
      self.isLoading = true
      let url = 'playlists/' + this.id + '/'
      axios.get(url).then((response) => {
        self.playlist = response.data
        axios.get(url + 'tracks/').then((response) => {
          self.updatePlts(response.data.results)
        }).then(() => {
          self.isLoading = false
        })
      })
    },
    deletePlaylist () {
      let self = this
      let url = 'playlists/' + this.id + '/'
      axios.delete(url).then((response) => {
        self.$store.dispatch('playlists/fetchOwn')
        self.$router.push({
          path: '/library'
        })
      })
    }
  }
}
</script>
