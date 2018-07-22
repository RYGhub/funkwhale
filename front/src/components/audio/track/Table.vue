<template>
  <table class="ui compact very basic fixed single line unstackable table">
    <thead>
      <tr>
        <th></th>
        <th></th>
        <th colspan="6"><translate>Title</translate></th>
        <th colspan="6"><translate>Artist</translate></th>
        <th colspan="6"><translate>Album</translate></th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <track-row
        :display-position="displayPosition"
        :track="track"
        :artist="artist"
        :key="index + '-' + track.id"
        v-for="(track, index) in tracks"></track-row>
    </tbody>
    <tfoot class="full-width">
      <tr>
        <th colspan="3">
          <button @click="showDownloadModal = !showDownloadModal" class="ui basic button">
             <translate>Download</translate>
          </button>
          <modal :show.sync="showDownloadModal">
            <div class="header"><translate>Download tracks</translate></div>
            <div class="content">
              <div class="description">
                <p><translate>There is currently no way to download directly multiple tracks from funkwhale as a ZIP archive. However, you can use a command line tools such as cURL to easily download a list of tracks.</translate></p>
                 <translate>Simply copy paste the snippet below into a terminal to launch the download.</translate>
                <div class="ui warning message">
                   <translate>Keep your PRIVATE_TOKEN secret as it gives access to your account.</translate>
                </div>
                <pre>
export PRIVATE_TOKEN="{{ $store.state.auth.token }}"
<template v-for="track in tracks"><template v-if="track.files.length > 0">
curl -G -o "{{ track.files[0].filename }}" <template v-if="$store.state.auth.authenticated">--header "Authorization: JWT $PRIVATE_TOKEN"</template> "{{ $store.getters['instance/absoluteUrl'](track.files[0].path) }}"</template></template>
</pre>
              </div>
            </div>
            <div class="actions">
              <div class="ui black deny button"><translate>Cancel</translate></div>
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

import TrackRow from '@/components/audio/track/Row'
import Modal from '@/components/semantic/Modal'

export default {
  props: {
    tracks: {type: Array, required: true},
    artist: {type: Object, required: false},
    displayPosition: {type: Boolean, default: false}
  },
  components: {
    Modal,
    TrackRow
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
pre {
  overflow-x: scroll;
}
</style>
