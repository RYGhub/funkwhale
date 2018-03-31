<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="'Artist'">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="artist">
      <div :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="artist.name">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted users violet icon"></i>
            <div class="content">
              {{ artist.name }}
              <div class="sub header">{{ totalTracks }} tracks in {{ albums.length }} albums</div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <radio-button type="artist" :object-id="artist.id"></radio-button>
          </button>
          <play-button class="orange" :tracks="allTracks">Play all albums</play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            Search on wikipedia
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            View on MusicBrainz
          </a>
        </div>
      </div>
      <div class="ui vertical stripe segment">
        <h2>Albums by this artist</h2>
        <div class="ui stackable doubling three column grid">
          <div class="column" :key="album.id" v-for="album in sortedAlbums">
            <album-card :mode="'rich'" class="fluid" :album="album"></album-card>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import logger from '@/logging'
import backend from '@/audio/backend'
import AlbumCard from '@/components/audio/album/Card'
import RadioButton from '@/components/radios/Button'
import PlayButton from '@/components/audio/PlayButton'

const FETCH_URL = 'artists/'

export default {
  props: ['id'],
  components: {
    AlbumCard,
    RadioButton,
    PlayButton
  },
  data () {
    return {
      isLoading: true,
      artist: null,
      albums: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      let url = FETCH_URL + this.id + '/'
      logger.default.debug('Fetching artist "' + this.id + '"')
      axios.get(url).then((response) => {
        self.artist = response.data
        self.albums = JSON.parse(JSON.stringify(self.artist.albums)).map((album) => {
          return backend.Album.clean(album)
        })
        self.isLoading = false
      })
    }
  },
  computed: {
    sortedAlbums () {
      let a = this.albums || []
      return _.orderBy(a, ['release_date'], ['asc'])
    },
    totalTracks () {
      return this.albums.map((album) => {
        return album.tracks.length
      }).reduce((a, b) => {
        return a + b
      })
    },
    wikipediaUrl () {
      return 'https://en.wikipedia.org/w/index.php?search=' + this.artist.name
    },
    musicbrainzUrl () {
      return 'https://musicbrainz.org/artist/' + this.artist.mbid
    },
    allTracks () {
      let tracks = []
      this.albums.forEach(album => {
        album.tracks.forEach(track => {
          tracks.push(track)
        })
      })
      return tracks
    },
    cover () {
      return this.artist.albums.filter(album => {
        return album.cover
      }).map(album => {
        return album.cover
      })[0]
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
<style scoped>
</style>
