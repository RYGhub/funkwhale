<template>
  <table class="ui compact very basic fixed single line unstackable table">
    <thead>
      <tr>
        <th></th>
        <th></th>
        <i18next tag="th" colspan="6" path="Title"/>
        <i18next tag="th" colspan="6" path="Artist"/>
        <i18next tag="th" colspan="6" path="Album"/>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <track-row
        :display-position="displayPosition"
        :track="track"
        :key="index + '-' + track.id"
        v-for="(track, index) in tracks"></track-row>
    </tbody>
    <tfoot class="full-width">
      <tr>
        <th colspan="3">
          <button @click="showDownloadModal = !showDownloadModal" class="ui basic button">
            <i18next path="Download..."/>
          </button>
          <modal :show.sync="showDownloadModal">
            <i18next tag="div" path="Download tracks" class="header" />
            <div class="content">
              <div class="description">
                <i18next tag="p" path="There is currently no way to download directly multiple tracks from funkwhale as a ZIP archive. However, you can use a command line tools such as {%0%} to easily download a list of tracks.">
                  <a href="https://curl.haxx.se/" target="_blank">cURL</a>
                </i18next>
                <i18next path="Simply copy paste the snippet below into a terminal to launch the download."/>
                <i18next tag="div" class="ui warning message" path="Keep your PRIVATE_TOKEN secret as it gives access to your account."/>
                <pre>
export PRIVATE_TOKEN="{{ $store.state.auth.token }}"
<template v-for="track in tracks"><template v-if="track.files.length > 0">
curl -G -o "{{ track.files[0].filename }}" <template v-if="$store.state.auth.authenticated">--header "Authorization: JWT $PRIVATE_TOKEN"</template> "{{ backend.absoluteUrl(track.files[0].path) }}"</template></template>
</pre>
              </div>
            </div>
            <div class="actions">
              <i18next tag="div" class="ui black deny button" path="Cancel" />
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
