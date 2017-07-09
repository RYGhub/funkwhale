<template>
  <div>
    <h3 class="ui dividing block header">
      Album <a :href="getMusicbrainzUrl('release', metadata.id)" target="_blank" title="View on MusicBrainz">{{ metadata.title }}</a> ({{ tracks.length}} tracks) by
      <a :href="getMusicbrainzUrl('artist', metadata['artist-credit'][0]['artist']['id'])" target="_blank" title="View on MusicBrainz">{{ metadata['artist-credit-phrase'] }}</a>
      <div class="ui divider"></div>
      <div class="sub header">
        <div class="ui toggle checkbox">
          <input type="checkbox" v-model="enabled" />
          <label>Import this release</label>
        </div>
      </div>
    </h3>
    <template
      v-if="enabled"
      v-for="track in tracks">
      <track-import
        :key="track.recording.id"
        :metadata="track"
        :release-metadata="metadata"
        :backends="backends"
        :default-backend-id="defaultBackendId"
        @import-data-changed="recordTrackData"
        @enabled="recordTrackEnabled"
      ></track-import>
      <div class="ui divider"></div>
    </template>
  </div>
</template>

<script>
import Vue from 'vue'
import ImportMixin from './ImportMixin'
import TrackImport from './TrackImport'

export default Vue.extend({
  mixins: [ImportMixin],
  components: {
    TrackImport
  },
  data () {
    return {
      trackImportData: []
    }
  },
  methods: {
    recordTrackData (track) {
      let existing = this.trackImportData.filter(t => {
        return t.mbid === track.mbid
      })[0]
      if (existing) {
        existing.source = track.source
      } else {
        this.trackImportData.push({
          mbid: track.mbid,
          enabled: true,
          source: track.source
        })
      }
    },
    recordTrackEnabled (track, enabled) {
      let existing = this.trackImportData.filter(t => {
        return t.mbid === track.mbid
      })[0]
      if (existing) {
        existing.enabled = enabled
      } else {
        this.trackImportData.push({
          mbid: track.mbid,
          enabled: enabled,
          source: null
        })
      }
    }
  },
  computed: {
    type () {
      return 'release'
    },
    importType () {
      return 'album'
    },
    tracks () {
      return this.metadata['medium-list'][0]['track-list']
    },
    importData () {
      let tracks = this.trackImportData.filter(t => {
        return t.enabled
      })
      return {
        releaseId: this.metadata.id,
        count: tracks.length,
        tracks: tracks
      }
    }
  },
  watch: {
    importData: {
      handler (newValue) {
        this.$emit('import-data-changed', newValue)
      },
      deep: true
    }
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.ui.card {
    width: 100% !important;
}
</style>
