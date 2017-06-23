<template>
  <div>
    <div v-if="isLoadingTrack" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="track">
      <div :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted music orange icon"></i>
            <div class="content">
              {{ track.title }}
              <div class="sub header">
                From album
                <router-link :to="{name: 'browse.album', params: {id: track.album.id }}">
                  {{ track.album.title }}
                </router-link>
                by <router-link :to="{name: 'browse.artist', params: {id: track.artist.id }}">
                  {{ track.artist.name }}
                </router-link>
              </div>
            </div>
          </h2>

          <play-button class="orange" :track="track">Play</play-button>
          <track-favorite-icon :track="track" :button="true"></track-favorite-icon>
          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            Search on wikipedia
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            View on MusicBrainz
          </a>
          <a v-if="downloadUrl" :href="downloadUrl" target="_blank" class="ui button">
            <i class="download icon"></i>
            Download
          </a>
        </div>
      </div>
      <div class="ui vertical stripe center aligned segment">
        <h2>Lyrics</h2>
        <div v-if="isLoadingLyrics" class="ui vertical segment">
          <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
        </div>
        <div v-if="lyrics" v-html="lyrics.content_rendered">
        </div>
        <template v-if="!isLoadingLyrics & !lyrics">
          <p>
            No lyrics available for this track.
          </p>
          <a class="ui button" target="_blank" :href="lyricsSearchUrl">
            <i class="search icon"></i>
            Search on lyrics.wikia.com
          </a>
        </template>
      </div>
    </template>
  </div>
</template>

<script>

import logger from '@/logging'
import backend from '@/audio/backend'
import PlayButton from '@/components/audio/PlayButton'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import config from '@/config'

const FETCH_URL = config.API_URL + 'tracks/'

export default {
  props: ['id'],
  components: {
    PlayButton,
    TrackFavoriteIcon
  },
  data () {
    return {
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
      this.$http.get(url).then((response) => {
        self.track = response.data
        self.isLoadingTrack = false
      })
    },
    fetchLyrics () {
      var self = this
      this.isLoadingLyrics = true
      let url = FETCH_URL + this.id + '/lyrics/'
      logger.default.debug('Fetching lyrics for track "' + this.id + '"')
      this.$http.get(url).then((response) => {
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
        return backend.absoluteUrl(this.track.files[0].path)
      }
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

</style>
