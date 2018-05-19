<template>
  <div>
    <div v-if="isLoadingTrack" class="ui vertical segment" v-title="'Track'">
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
                <i18next path="From album {%0%} by {%1%}">
                  <router-link :to="{name: 'library.albums.detail', params: {id: track.album.id }}">
                    {{ track.album.title }}
                  </router-link>
                  <router-link :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
                    {{ track.artist.name }}
                  </router-link>
                </i18next>
              </div>
            </div>
          </h2>

          <play-button class="orange" :track="track"><i18next path="Play"/></play-button>
          <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
          <track-playlist-icon
            :button="true"
            v-if="$store.state.auth.authenticated"
            :track="track"></track-playlist-icon>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <i18next path="Search on Wikipedia"/>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <i18next path="View on MusicBrainz"/>
          </a>
          <a v-if="downloadUrl" :href="downloadUrl" target="_blank" class="ui button">
            <i class="download icon"></i>
            <i18next path="Download"/>
          </a>
        </div>
      </div>
      <div v-if="file" class="ui vertical stripe center aligned segment">
        <h2 class="ui header">{{ $t('Track information') }}</h2>
        <table class="ui very basic collapsing celled center aligned table">
          <tbody>
            <tr>
              <td>
                {{ $t('Duration') }}
              </td>
              <td v-if="file.duration">
                {{ time.parse(file.duration) }}
              </td>
              <td v-else>
                {{ $t('N/A') }}
              </td>
            </tr>
            <tr>
              <td>
                {{ $t('Size') }}
              </td>
              <td v-if="file.size">
                {{ file.size | humanSize }}
              </td>
              <td v-else>
                {{ $t('N/A') }}
              </td>
            </tr>
            <tr>
              <td>
                {{ $t('Bitrate') }}
              </td>
              <td v-if="file.bitrate">
                {{ file.bitrate | humanSize }}/s
              </td>
              <td v-else>
                {{ $t('N/A') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="ui vertical stripe center aligned segment">
        <h2><i18next path="Lyrics"/></h2>
        <div v-if="isLoadingLyrics" class="ui vertical segment">
          <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
        </div>
        <div v-if="lyrics" v-html="lyrics.content_rendered">
        </div>
        <template v-if="!isLoadingLyrics & !lyrics">
          <i18next tag="p" path="No lyrics available for this track."/>
          <a class="ui button" target="_blank" :href="lyricsSearchUrl">
            <i class="search icon"></i>
            <i18next path="Search on lyrics.wikia.com"/>
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
import backend from '@/audio/backend'
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
    wikipediaUrl () {
      return 'https://en.wikipedia.org/w/index.php?search=' + this.track.title + ' ' + this.track.artist.name
    },
    musicbrainzUrl () {
      return 'https://musicbrainz.org/recording/' + this.track.mbid
    },
    downloadUrl () {
      if (this.track.files.length > 0) {
        let u = backend.absoluteUrl(this.track.files[0].path)
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
      return 'background-image: url(' + backend.absoluteUrl(this.cover) + ')'
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
