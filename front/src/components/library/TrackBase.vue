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
                <div translate-context="Content/Track/Paragraph"
                  v-translate="{album: track.album.title, artist: track.artist.name, albumUrl: albumUrl, artistUrl: artistUrl}"
                >From album <a class="internal" href="%{ albumUrl }">%{ album }</a> by <a class="internal" href="%{ artistUrl }">%{ artist }</a></div>
              </div>
            </div>
          </h2>

          <play-button class="orange" :track="track">
            <translate translate-context="*/Queue/Button.Label/Short, Verb">Play</translate>
          </play-button>
          <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
          <track-playlist-icon :button="true" v-if="$store.state.auth.authenticated" :track="track"></track-playlist-icon>

          <a :href="wikipediaUrl" target="_blank" class="ui icon labeled button">
            <i class="wikipedia w icon"></i>
            <translate translate-context="Content/*/Link/Verb">Search on Wikipedia</translate>
          </a>
          <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" class="ui icon labeled button">
            <i class="external icon"></i>
            <translate translate-context="Content/*/Link/Verb">View on MusicBrainz</translate>
          </a>
          <a v-if="upload" :href="downloadUrl" target="_blank" class="ui icon labeled button">
            <i class="download icon"></i>
            <translate translate-context="Content/Track/Link/Verb">Download</translate>
          </a>
          <template v-if="publicLibraries.length > 0">
            <button
              @click="showEmbedModal = !showEmbedModal"
              class="ui icon labeled button">
              <i class="code icon"></i>
              <translate translate-context="Content/Track/Button.Label/Verb">Embed</translate>
            </button>
            <modal :show.sync="showEmbedModal">
              <div class="header">
                <translate translate-context="Popup/Track/Title">Embed this track on your website</translate>
              </div>
              <div class="content">
                <div class="description">
                  <embed-wizard type="track" :id="track.id" />

                </div>
              </div>
              <div class="actions">
                <div class="ui deny button">
                  <translate translate-context="Popup/Track/Button/Verb">Cancel</translate>
                </div>
              </div>
            </modal>
          </template>
          <router-link
            :to="{name: 'library.tracks.edit', params: {id: track.id }}"
            class="ui icon labeled button">
            <i class="edit icon"></i>
            <translate translate-context="Content/Track/Button.Label/Verb">Edit…</translate>
          </router-link>
        </div>
      </section>
      <router-view v-if="track" @libraries-loaded="libraries = $event" :track="track" :object="track" object-type="track" :key="$route.fullPath"></router-view>
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
import Modal from '@/components/semantic/Modal'
import EmbedWizard from "@/components/audio/EmbedWizard"

const FETCH_URL = "tracks/"

export default {
  props: ["id"],
  components: {
    PlayButton,
    TrackPlaylistIcon,
    TrackFavoriteIcon,
    Modal,
    EmbedWizard
  },
  data() {
    return {
      time,
      isLoadingTrack: true,
      track: null,
      showEmbedModal: false,
      libraries: []
    }
  },
  created() {
    this.fetchData()
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
  },
  computed: {
    publicLibraries () {
      return this.libraries.filter(l => {
        return l.privacy_level === 'everyone'
      })
    },
    upload() {
      if (this.track.uploads) {
        return this.track.uploads[0]
      }
    },
    labels() {
      return {
        title: this.$pgettext('Head/Track/Title', "Track")
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
      return u
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
  },
  watch: {
    id() {
      this.fetchData()
    },
  }
}
</script>
