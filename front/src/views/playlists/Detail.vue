<template>
  <div v-if="playlist">
    <div class="ui head vertical center aligned stripe segment">
      <div class="segment-content">
        <h2 class="ui center aligned icon header">
          <i class="circular inverted list yellow icon"></i>
          <div class="content">
            {{ playlist.name }}
            <div class="sub header">
              Playlist containing {{ playlistTracks.length }} tracks,
              by <username :username="playlist.user.username"></username>
            </div>
          </div>
        </h2>
        <div class="ui hidden divider"></div>
        </button>
        <play-button class="orange" :tracks="tracks">Play all</play-button>
        <button
          class="ui icon button"
          v-if="playlist.user.id === $store.state.auth.profile.id"
          @click="edit = !edit">
          <i class="pencil icon"></i>
          <template v-if="edit">End edition</template>
          <template v-else>Edit...</template>
        </button>
      </div>
    </div>
    <div v-if="tracks.length > 0" class="ui vertical stripe segment">
      <template v-if="edit">
        <playlist-editor @tracks-updated="updatePlts" :playlist="playlist" :playlist-tracks="playlistTracks"></playlist-editor>
      </template>
      <template v-else>
        <h2>Tracks</h2>
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
    id: {required: true}
  },
  components: {
    PlaylistEditor,
    TrackTable,
    PlayButton,
    RadioButton
  },
  data: function () {
    return {
      edit: false,
      playlist: null,
      tracks: [],
      playlistTracks: []
    }
  },
  created: function () {
    this.fetch()
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
      let url = 'playlists/' + this.id + '/'
      axios.get(url).then((response) => {
        self.playlist = response.data
        axios.get(url + 'tracks').then((response) => {
          self.updatePlts(response.data.results)
        })
      })
    }
  }
}
</script>
