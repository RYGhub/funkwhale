<template>
  <main>
    <div v-if="isLoadingTrack" class="ui vertical segment" v-title="labels.title">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="track">
      <section
        :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']"
        :style="headerStyle"
        v-title="track.title"
      >
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted music orange icon"></i>
            <div class="content">
              {{ track.title }}
              <div class="sub header">
                <div :translate-context="'Content/Track/Paragraph'"
                  v-translate="{album: track.album.title, artist: track.artist.name, albumUrl: albumUrl, artistUrl: artistUrl}"
                >From album <a class="internal" href="%{ albumUrl }">%{ album }</a> by <a class="internal" href="%{ artistUrl }">%{ artist }</a></div>
              </div>
            </div>
          </h2>

          <play-button class="orange" :track="track">
            <translate :translate-context="'*/Queue/Button.Label/Short, Verb'">Play</translate>
          </play-button>
          <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
          <track-playlist-icon :button="true" v-if="$store.state.auth.authenticated" :track="track"></track-playlist-icon>

          <a :href="wikipediaUrl" target="_blank" class="ui icon labeled button">
            <i class="wikipedia w icon"></i>
            <translate :translate-context="'Content/*/Link/Verb'">Search on Wikipedia</translate>
          </a>
          <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" class="ui icon labeled button">
            <i class="external icon"></i>
            <translate :translate-context="'Content/*/Link/Verb'">View on MusicBrainz</translate>
          </a>
          <a v-if="upload" :href="downloadUrl" target="_blank" class="ui icon labeled button">
            <i class="download icon"></i>
            <translate :translate-context="'Content/Track/Link/Verb'">Download</translate>
          </a>
          <template v-if="publicLibraries.length > 0">
            <button
              @click="showEmbedModal = !showEmbedModal"
              class="ui icon labeled button">
              <i class="code icon"></i>
              <translate :translate-context="'Content/Track/Button.Label/Verb'">Embed</translate>
            </button>
            <modal :show.sync="showEmbedModal">
              <div class="header">
                <translate :translate-context="'Popup/Track/Title'">Embed this track on your website</translate>
              </div>
              <div class="content">
                <div class="description">
                  <embed-wizard type="track" :id="track.id" />

                </div>
              </div>
              <div class="actions">
                <div class="ui deny button">
                  <translate :translate-context="'Popup/Track/Button/Verb'">Cancel</translate>
                </div>
              </div>
            </modal>
          </template>
        </div>
      </section>
      <section class="ui vertical stripe center aligned segment">
        <h2 class="ui header">
          <translate :translate-context="'Content/Track/Title/Noun'">Track information</translate>
        </h2>
        <table class="ui very basic collapsing celled center aligned table">
          <tbody>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label/Noun'">Copyright</translate>
              </td>
              <td v-if="track.copyright" :title="track.copyright">{{ track.copyright|truncate(50) }}</td>
              <td v-else>
                <translate :translate-context="'Content/Track/Table.Paragraph'">No copyright information available for this track</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label/Noun'">License</translate>
              </td>
              <td v-if="license">
                <a :href="license.url" target="_blank" rel="noopener noreferrer">{{ license.name }}</a>
              </td>
              <td v-else>
                <translate :translate-context="'Content/Track/Table.Paragraph'">No licensing information for this track</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label'">Duration</translate>
              </td>
              <td v-if="upload && upload.duration">{{ time.parse(upload.duration) }}</td>
              <td v-else>
                <translate :translate-context="'*/*/*'">N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label'">Size</translate>
              </td>
              <td v-if="upload && upload.size">{{ upload.size | humanSize }}</td>
              <td v-else>
                <translate :translate-context="'*/*/*'">N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label'">Bitrate</translate>
              </td>
              <td v-if="upload && upload.bitrate">{{ upload.bitrate | humanSize }}/s</td>
              <td v-else>
                <translate :translate-context="'*/*/*'">N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate :translate-context="'Content/Track/Table.Label/Noun'">Type</translate>
              </td>
              <td v-if="upload && upload.extension">{{ upload.extension }}</td>
              <td v-else>
                <translate :translate-context="'*/*/*'">N/A</translate>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
      <section class="ui vertical stripe center aligned segment">
        <h2>
          <translate :translate-context="'Content/Track/Title'">Lyrics</translate>
        </h2>
        <div v-if="isLoadingLyrics" class="ui vertical segment">
          <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
        </div>
        <div v-if="lyrics" v-html="lyrics.content_rendered"></div>
        <template v-if="!isLoadingLyrics & !lyrics">
          <p>
            <translate :translate-context="'Content/Track/Paragraph'">No lyrics available for this track.</translate>
          </p>
          <a class="ui button" target="_blank" :href="lyricsSearchUrl">
            <i class="search icon"></i>
            <translate :translate-context="'Content/Track/Link/Verb'">Search on lyrics.wikia.com</translate>
          </a>
        </template>
      </section>
      <section class="ui vertical stripe segment">
        <h2>
          <translate :translate-context="'Content/Track/Title'">User libraries</translate>
        </h2>
        <library-widget @loaded="libraries = $event" :url="'tracks/' + id + '/libraries/'">
          <translate :translate-context="'Content/Track/Paragraph'" slot="subtitle">This track is present in the following libraries:</translate>
        </library-widget>
      </section>
    </template>
  </main>
</template>

<script>
import time from "@/utils/time"
import axios from "axios"
import url from "@/utils/url"
import logger from "@/logging"
import PlayButton from "@/components/audio/PlayButton"
import TrackFavoriteIcon from "@/components/favorites/TrackFavoriteIcon"
import TrackPlaylistIcon from "@/components/playlists/TrackPlaylistIcon"
import LibraryWidget from "@/components/federation/LibraryWidget"
import Modal from '@/components/semantic/Modal'
import EmbedWizard from "@/components/audio/EmbedWizard"

const FETCH_URL = "tracks/"

export default {
  props: ["id"],
  components: {
    PlayButton,
    TrackPlaylistIcon,
    TrackFavoriteIcon,
    LibraryWidget,
    Modal,
    EmbedWizard
  },
  data() {
    return {
      time,
      isLoadingTrack: true,
      isLoadingLyrics: true,
      track: null,
      lyrics: null,
      licenseData: null,
      libraries: [],
      showEmbedModal: false
    }
  },
  created() {
    this.fetchData()
    this.fetchLyrics()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoadingTrack = true
      let url = FETCH_URL + this.id + "/"
      logger.default.debug('Fetching track "' + this.id + '"')
      axios.get(url).then(response => {
        self.track = response.data
        self.isLoadingTrack = false
      })
    },
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
    publicLibraries () {
      return this.libraries.filter(l => {
        return l.privacy_level === 'everyone'
      })
    },
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
    wikipediaUrl() {
      return (
        "https://en.wikipedia.org/w/index.php?search=" +
        encodeURI(this.track.title + " " + this.track.artist.name)
      )
    },
    musicbrainzUrl() {
      if (this.track.mbid) {
        return "https://musicbrainz.org/recording/" + this.track.mbid
      }
    },
    downloadUrl() {
      let u = this.$store.getters["instance/absoluteUrl"](
        this.upload.listen_url
      )
      if (this.$store.state.auth.authenticated) {
        u = url.updateQueryString(
          u,
          "jwt",
          encodeURI(this.$store.state.auth.token)
        )
      }
      return u
    },
    lyricsSearchUrl() {
      let base = "http://lyrics.wikia.com/wiki/Special:Search?query="
      let query = this.track.artist.name + ":" + this.track.title
      return base + encodeURI(query)
    },
    cover() {
      return null
    },
    albumUrl () {
      let route = this.$router.resolve({name: 'library.albums.detail', params: {id: this.track.album.id }})
      return route.location.path
    },
    artistUrl () {
      let route = this.$router.resolve({name: 'library.artists.detail', params: {id: this.track.artist.id }})
      return route.location.path
    },
    headerStyle() {
      if (!this.cover) {
        return ""
      }
      return (
        "background-image: url(" +
        this.$store.getters["instance/absoluteUrl"](this.cover) +
        ")"
      )
    },
    license() {
      if (!this.track || !this.track.license) {
        return null
      }
      return this.licenseData
    }
  },
  watch: {
    id() {
      this.fetchData()
    },
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
