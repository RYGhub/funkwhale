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
              <translate translate-context="Content/Track/Table.Label/Noun">Copyright</translate>
            </td>
            <td v-if="track.copyright" :title="track.copyright">{{ track.copyright|truncate(50) }}</td>
            <td v-else>
              <translate translate-context="Content/Track/Table.Paragraph">No copyright information available for this track</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/Track/Table.Label/Noun">License</translate>
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
              <translate translate-context="Content/Track/Table.Label">Duration</translate>
            </td>
            <td v-if="upload && upload.duration">{{ time.parse(upload.duration) }}</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/Track/Table.Label">Size</translate>
            </td>
            <td v-if="upload && upload.size">{{ upload.size | humanSize }}</td>
            <td v-else>
              <translate translate-context="*/*/*">N/A</translate>
            </td>
          </tr>
          <tr>
            <td>
              <translate translate-context="Content/Track/Table.Label">Bitrate</translate>
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
        </tbody>
      </table>
    </section>
    <section class="ui vertical stripe center aligned segment">
      <h2>
        <translate translate-context="Content/Track/Title">Lyrics</translate>
      </h2>
      <div v-if="isLoadingLyrics" class="ui vertical segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <div v-if="lyrics" v-html="lyrics.content_rendered"></div>
      <template v-if="!isLoadingLyrics & !lyrics">
        <p>
          <translate translate-context="Content/Track/Paragraph">No lyrics available for this track.</translate>
        </p>
        <a class="ui button" target="_blank" :href="lyricsSearchUrl">
          <i class="search icon"></i>
          <translate translate-context="Content/Track/Link/Verb">Search on lyrics.wikia.com</translate>
        </a>
      </template>
    </section>
    <section class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/Track/Title">User libraries</translate>
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
      isLoadingLyrics: true,
      lyrics: null,
      licenseData: null
    }
  },
  created() {
    this.fetchLyrics()
    if (this.track && this.track.license) {
      this.fetchLicenseData(this.track.license)
    }
  },
  methods: {
    fetchLicenseData(licenseId) {
      var self = this
      let url = `licenses/${licenseId}/`
      axios.get(url).then(response => {
        self.licenseData = response.data
      })
    },
    fetchLyrics() {
      var self = this
      this.isLoadingLyrics = true
      let url = FETCH_URL + this.id + "/lyrics/"
      logger.default.debug('Fetching lyrics for track "' + this.id + '"')
      axios.get(url).then(
        response => {
          self.lyrics = response.data
          self.isLoadingLyrics = false
        },
        response => {
          console.error("No lyrics available")
          self.isLoadingLyrics = false
        }
      )
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('Head/Track/Title', "Track")
      }
    },
    upload() {
      if (this.track.uploads) {
        return this.track.uploads[0]
      }
    },
    lyricsSearchUrl() {
      let base = "http://lyrics.wikia.com/wiki/Special:Search?query="
      let query = this.track.artist.name + ":" + this.track.title
      return base + encodeURI(query)
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
