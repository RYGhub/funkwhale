<template>
  <modal @update:show="update" :show="show">
    <div class="header">
      Add track "{{ track.title }}" by {{ track.artist.name }} to playlist
    </div>
    <div class="content">
      <div class="description">
        <playlist-form></playlist-form>
        <div class="ui divider"></div>
        <div v-if="errors.length > 0" class="ui negative message">
          <div class="header">We cannot add the track to a playlist</div>
          <ul class="list">
            <li v-for="error in errors">{{ error }}</li>
          </ul>
        </div>
        <div class="ui items">
          <div class="item" v-for="playlist in sortedPlaylists">
            <div class="content">
              <div class="header">{{ playlist.name }}</div>
              <div class="meta">
                <span class="tracks"><i class="music icon"></i> {{ playlist.tracks_count }} tracks</span>
                <span class="date"><i class="clock icon"></i> Last modification {{ playlist.modification_date | ago}}</span>
              </div>
              <div class="extra">
                <div class="ui basic green button" @click="addToPlaylist(playlist.id)">
                  Add to this playlist
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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
  props: {
    track: {type: Object},
    show: {type: Boolean}
  },
  data () {
    return {
      errors: []
    }
  },
  methods: {
    update (v) {
      this.$emit('update:show', v)
    },
    addToPlaylist (playlistId) {
      let self = this
      let payload = {
        track: this.track.id,
        playlist: playlistId
      }
      return axios.post('playlist-tracks/', payload).then(response => {
        logger.default.info('Successfully added track to playlist')
        self.$emit('update:show', false)
        self.$store.dispatch('playlists/fetchOwn')
      }, error => {
        logger.default.error('Error while adding track to playlist')
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    ...mapState({
      playlists: state => state.playlists.playlists
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
