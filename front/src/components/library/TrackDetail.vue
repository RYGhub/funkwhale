<template>

  <div v-if="track">
    <section class="ui vertical stripe center aligned segment">
      <h2 class="ui header">
        <translate translate-context="Content/Track/Title/Noun">Track information</translate>
      </h2>
      <table class="ui very basic collapsing celled center aligned table">
        <tbody>
          <tr>
            <td>
              <translate translate-context="Content/Track/*/Noun">Copyright</translate>
            </td>
            <td v-if="track.copyright" :title="track.copyright">{{ track.copyright|truncate(50) }}</td>
            <td v-else>
              <translate translate-context="Content/Track/Table.Paragraph">No copyright information available for this track</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/*/*/Noun">License</translate>
            </td>
            <td v-if="license">
              <a :href="license.url" target="_blank" rel="noopener noreferrer">{{ license.name }}</a>
            </td>
            <td v-else>
              <translate translate-context="Content/Track/Table.Paragraph">No licensing information for this track</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/*/*">Duration</translate>
            </td>
            <td v-if="upload && upload.duration">{{ time.parse(upload.duration) }}</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/*/*/Noun">Size</translate>
            </td>
            <td v-if="upload && upload.size">{{ upload.size | humanSize }}</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/Track/*/Noun">Bitrate</translate>
            </td>
            <td v-if="upload && upload.bitrate">{{ upload.bitrate | humanSize }}/s</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/Track/Table.Label/Noun">Type</translate>
            </td>
            <td v-if="upload && upload.extension">{{ upload.extension }}</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/*/*/Noun">Federation ID</translate>
            </td>
            <td :title="track.fid">
              <a :href="track.fid" target="_blank" rel="noopener noreferrer">
                {{ track.fid|truncate(65)}}
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
    <section class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/*/Title/Noun">User libraries</translate>
      </h2>
      <library-widget @loaded="$emit('libraries-loaded', $event)" :url="'tracks/' + id + '/libraries/'">
        <translate translate-context="Content/Track/Paragraph" slot="subtitle">This track is present in the following libraries:</translate>
      </library-widget>
    </section>
  </div>
</template>

<script>
import time from "@/utils/time"
import axios from "axios"
import url from "@/utils/url"
import logger from "@/logging"
import LibraryWidget from "@/components/federation/LibraryWidget"

const FETCH_URL = "tracks/"

export default {
  props: ["track", "libraries"],
  components: {
    LibraryWidget,
  },
  data() {
    return {
      time,
      id: this.track.id,
      licenseData: null
    }
  },
  created() {
    if (this.track && this.track.license) {
      this.fetchLicenseData(this.track.license)
    }
  },
  methods: {
    fetchLicenseData(licenseId) {
      var self = this
      let url = `licenses/${licenseId}`
      axios.get(url).then(response => {
        self.licenseData = response.data
      })
    },
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*/Noun', "Track")
      }
    },
    upload() {
      if (this.track.uploads) {
        return this.track.uploads[0]
      }
    },
    license() {
      if (!this.track || !this.track.license) {
        return null
      }
      return this.licenseData
    }
  },
  watch: {
    track (v) {
      if (v && v.license) {
        this.fetchLicenseData(v.license)
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.table.center.aligned {
  margin-left: auto;
  margin-right: auto;
}
</style>
