<template>
  <table class="ui compact very basic fixed single line unstackable table">
    <thead>
      <tr>
        <th></th>
        <th></th>
        <th colspan="6">Title</th>
        <th colspan="6">Artist</th>
        <th colspan="6">Album</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="track in tracks">
        <td>
          <play-button class="basic icon" :discrete="true" :track="track"></play-button>
        </td>
        <td>
          <img class="ui mini image" v-if="track.album.cover" v-lazy="backend.absoluteUrl(track.album.cover)">
          <img class="ui mini image" v-else src="../../..//assets/audio/default-cover.png">
        </td>
        <td colspan="6">
          <router-link class="track" :to="{name: 'library.tracks.detail', params: {id: track.id }}">
            <template v-if="displayPosition && track.position">
              {{ track.position }}.
            </template>
            {{ track.title }}
          </router-link>
        </td>
        <td colspan="6">
          <router-link class="artist discrete link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
            {{ track.artist.name }}
          </router-link>
        </td>
        <td colspan="6">
          <router-link class="album discrete link" :to="{name: 'library.albums.detail', params: {id: track.album.id }}">
            {{ track.album.title }}
          </router-link>
        </td>
        <td><track-favorite-icon class="favorite-icon" :track="track"></track-favorite-icon></td>
      </tr>
    </tbody>
    <tfoot class="full-width">
      <tr>
        <th colspan="3">
          <button @click="showDownloadModal = !showDownloadModal" class="ui basic button">Download...</button>
          <modal :show.sync="showDownloadModal">
            <div class="header">
              Download tracks
            </div>
            <div class="content">
              <div class="description">
                <p>There is currently no way to download directly multiple tracks from funkwhale as a ZIP archive.
                  However, you can use a command line tools such as <a href="https://curl.haxx.se/" target="_blank">cURL</a> to easily download a list of tracks.
                </p>
                <p>Simply copy paste the snippet below into a terminal to launch the download.</p>
                <div class="ui warning message">
                  Keep your PRIVATE_TOKEN secret as it gives access to your account.
                </div>
                <pre>
export PRIVATE_TOKEN="{{ $store.state.auth.token }}"
<template v-for="track in tracks"><template v-if="track.files.length > 0">
curl -G -o "{{ track.files[0].filename }}" <template v-if="$store.state.auth.authenticated">--header "Authorization: JWT $PRIVATE_TOKEN"</template> "{{ backend.absoluteUrl(track.files[0].path) }}"</template></template>
</pre>
              </div>
            </div>
            <div class="actions">
              <div class="ui black deny button">
                Cancel
              </div>
            </div>
          </modal>
        </th>
        <th></th>
        <th colspan="4"></th>
        <th colspan="6"></th>
        <th colspan="6"></th>
        <th></th>
      </tr>
    </tfoot>
  </table>
</template>

<script>
import backend from '@/audio/backend'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import PlayButton from '@/components/audio/PlayButton'

import Modal from '@/components/semantic/Modal'

export default {
  props: {
    tracks: {type: Array, required: true},
    displayPosition: {type: Boolean, default: false}
  },
  components: {
    Modal,
    TrackFavoriteIcon,
    PlayButton
  },
  data () {
    return {
      backend: backend,
      showDownloadModal: false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

tr:not(:hover) .favorite-icon:not(.favorited) {
  display: none;
}
</style>
