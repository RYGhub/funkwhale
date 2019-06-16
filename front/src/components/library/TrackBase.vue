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
              <div class="sub header" v-html="subtitle"></div>
            </div>
          </h2>
          <div class="header-buttons">
            <div class="ui buttons">
              <play-button class="orange" :track="track">
                <translate translate-context="*/Queue/Button.Label/Short, Verb">Play</translate>
              </play-button>
            </div>
            <div class="ui buttons">
              <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
            </div>
            <div class="ui buttons">
              <track-playlist-icon :button="true" v-if="$store.state.auth.authenticated" :track="track"></track-playlist-icon>
            </div>

            <div class="ui buttons">
              <a v-if="upload" :href="downloadUrl" target="_blank" class="ui icon labeled button">
                <i class="download icon"></i>
                <translate translate-context="Content/Track/Link/Verb">Download</translate>
              </a>
            </div>

            <modal v-if="publicLibraries.length > 0" :show.sync="showEmbedModal">
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
                  <translate translate-context="*/*/Button.Label/Verb">Cancel</translate>
                </div>
              </div>
            </modal>
            <div class="ui buttons">
              <button class="ui button" @click="$refs.dropdown.click()">
                <translate translate-context="*/*/Button.Label/Noun">More…</translate>
              </button>
              <div class="ui floating dropdown icon button" ref="dropdown" v-dropdown>
                <i class="dropdown icon"></i>
                <div class="menu">
                  <div
                    role="button"
                    v-if="publicLibraries.length > 0"
                    @click="showEmbedModal = !showEmbedModal"
                    class="basic item">
                    <i class="code icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Embed</translate>
                  </div>
                  <a :href="wikipediaUrl" target="_blank" rel="noreferrer noopener" class="basic item">
                    <i class="wikipedia w icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Search on Wikipedia</translate>
                  </a>
                  <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" rel="noreferrer noopener" class="basic item">
                    <i class="external icon"></i>
                    <translate translate-context="Content/*/*/Clickable, Verb">View on MusicBrainz</translate>
                  </a>
		  <a :href="discogsUrl" target="_blank" rel="noreferrer noopener" class="basic item">
		    <i class="external icon"></i>
		    <translate translate-context="Content/*/Button.Label/Verb">Search on Discogs</translate>
		  </a>
                  <router-link
                    v-if="track.is_local"
                    :to="{name: 'library.tracks.edit', params: {id: track.id }}"
                    class="basic item">
                    <i class="edit icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Edit</translate>
                  </router-link>
                  <div class="divider"></div>
                  <router-link class="basic item" v-if="$store.state.auth.availablePermissions['library']" :to="{name: 'manage.library.tracks.detail', params: {id: track.id}}">
                    <i class="wrench icon"></i>
                    <translate translate-context="Content/Moderation/Link">Open in moderation interface</translate>
                  </router-link>
                  <a
                    v-if="$store.state.auth.profile && $store.state.auth.profile.is_superuser"
                    class="basic item"
                    :href="$store.getters['instance/absoluteUrl'](`/api/admin/music/track/${track.id}`)"
                    target="_blank" rel="noopener noreferrer">
                    <i class="wrench icon"></i>
                    <translate translate-context="Content/Moderation/Link/Verb">View in Django's admin</translate>&nbsp;
                  </a>
                </div>
              </div>
            </div>
          </div>
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
        title: this.$pgettext('*/*/*/Noun', "Track")
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
    discogsUrl() {
      return (
        "https://discogs.com/search/?type=release&title=" +
	encodeURI(this.track.album.title) + "&artist=" +
	encodeURI(this.track.artist.name) + "&track=" +
	encodeURI(this.track.title)
      )
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
    subtitle () {
      let msg = this.$pgettext('Content/Track/Paragraph', 'From album <a class="internal" href="%{ albumUrl }">%{ album }</a> by <a class="internal" href="%{ artistUrl }">%{ artist }</a>')
      return this.$gettextInterpolate(msg, {album: this.track.album.title, artist: this.track.artist.name, albumUrl: this.albumUrl, artistUrl: this.artistUrl})
    }
  },
  watch: {
    id() {
      this.fetchData()
    },
  }
}
</script>
