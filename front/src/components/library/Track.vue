<template>
  <div>
    <div v-if="isLoadingTrack" class="ui vertical segment" v-title="labels.title">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="track">
      <div :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="track.title">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted music orange icon"></i>
            <div class="content">
              {{ track.title }}
              <div class="sub header">
                <translate :translate-params="{album: track.album.title, artist: track.artist.name}">
                  From album %{ album } by %{ artist }
                </translate>
              </div>
              <br>
              <div class="ui basic buttons">
                <router-link class="ui button" :to="{name: 'library.albums.detail', params: {id: track.album.id }}">
                  <translate>Album page</translate>
                </router-link>
                <router-link class="ui button" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
                  <translate>Artist page</translate>
                </router-link>
              </div>
            </div>
          </h2>

          <play-button class="orange" :track="track">
            <translate>Play</translate>
          </play-button>
          <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
          <track-playlist-icon
            :button="true"
            v-if="$store.state.auth.authenticated"
            :track="track"></track-playlist-icon>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <translate>Search on Wikipedia</translate>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <translate>View on MusicBrainz</translate>
          </a>
          <a v-if="downloadUrl" :href="downloadUrl" target="_blank" class="ui button">
            <i class="download icon"></i>
            <translate>Download</translate>
          </a>
        </div>
      </div>
      <div v-if="file" class="ui vertical stripe center aligned segment">
        <h2 class="ui header"><translate>Track information</translate></h2>
        <table class="ui very basic collapsing celled center aligned table">
          <tbody>
            <tr>
              <td>
                <translate>Duration</translate>
              </td>
              <td v-if="file.duration">
                {{ time.parse(file.duration) }}
              </td>
              <td v-else>
                <translate>N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate>Size</translate>
              </td>
              <td v-if="file.size">
                {{ file.size | humanSize }}
              </td>
              <td v-else>
                <translate>N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate>Bitrate</translate>
              </td>
              <td v-if="file.bitrate">
                {{ file.bitrate | humanSize }}/s
              </td>
              <td v-else>
                <translate>N/A</translate>
              </td>
            </tr>
            <tr>
              <td>
                <translate>Type</translate>
              </td>
              <td v-if="file.mimetype">
                {{ file.mimetype }}
              </td>
              <td v-else>
                <translate>N/A</translate>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="ui vertical stripe center aligned segment">
        <h2>
          <translate>Lyrics</translate>
        </h2>
        <div v-if="isLoadingLyrics" class="ui vertical segment">
          <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
        </div>
        <div v-if="lyrics" v-html="lyrics.content_rendered">
        </div>
        <template v-if="!isLoadingLyrics & !lyrics">
          <p><translate>No lyrics available for this track.</translate></p>
          <a class="ui button" target="_blank" :href="lyricsSearchUrl">
            <i class="search icon"></i>
            <translate>Search on lyrics.wikia.com</translate>
          </a>
        </template>
      </div>
    </template>
  </div>
</template>

<script>

import time from '@/utils/time'
import axios from 'axios'
import url from '@/utils/url'
import logger from '@/logging'
import PlayButton from '@/components/audio/PlayButton'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import TrackPlaylistIcon from '@/components/playlists/TrackPlaylistIcon'

const FETCH_URL = 'tracks/'

export default {
  props: ['id'],
  components: {
    PlayButton,
    TrackPlaylistIcon,
    TrackFavoriteIcon
  },
  data () {
    return {
      time,
      isLoadingTrack: true,
      isLoadingLyrics: true,
      track: null,
      lyrics: null
    }
  },
  created () {
    this.fetchData()
    this.fetchLyrics()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoadingTrack = true
      let url = FETCH_URL + this.id + '/'
      logger.default.debug('Fetching track "' + this.id + '"')
      axios.get(url).then((response) => {
        self.track = response.data
        self.isLoadingTrack = false
      })
    },
    fetchLyrics () {
      var self = this
      this.isLoadingLyrics = true
      let url = FETCH_URL + this.id + '/lyrics/'
      logger.default.debug('Fetching lyrics for track "' + this.id + '"')
      axios.get(url).then((response) => {
        self.lyrics = response.data
        self.isLoadingLyrics = false
      }, (response) => {
        console.error('No lyrics available')
        self.isLoadingLyrics = false
      })
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Track')
      }
    },
    wikipediaUrl () {
      return 'https://en.wikipedia.org/w/index.php?search=' + this.track.title + ' ' + this.track.artist.name
    },
    musicbrainzUrl () {
      return 'https://musicbrainz.org/recording/' + this.track.mbid
    },
    downloadUrl () {
      if (this.track.files.length > 0) {
        let u = this.$store.getters['instance/absoluteUrl'](this.track.files[0].path)
        if (this.$store.state.auth.authenticated) {
          u = url.updateQueryString(u, 'jwt', this.$store.state.auth.token)
        }
        return u
      }
    },
    file () {
      return this.track.files[0]
    },
    lyricsSearchUrl () {
      let base = 'http://lyrics.wikia.com/wiki/Special:Search?query='
      let query = this.track.artist.name + ' ' + this.track.title
      return base + query
    },
    cover () {
      return null
    },
    headerStyle () {
      if (!this.cover) {
        return ''
      }
      return 'background-image: url(' + this.$store.getters['instance/absoluteUrl'](this.cover) + ')'
    }
  },
  watch: {
    id () {
      this.fetchData()
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
