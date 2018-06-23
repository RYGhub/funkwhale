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
              <div class="sub header" v-if="albums">
                {{ $t('{% track_count %} tracks in {% album_count %} albums', {track_count: totalTracks, album_count: albums.length})}}
              </div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <radio-button type="artist" :object-id="artist.id"></radio-button>
          </button>
          <play-button class="orange" :artist="artist.id"><i18next path="Play all albums"/></play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <i18next path="Search on Wikipedia"/>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <i18next path="View on MusicBrainz"/>
          </a>
        </div>
      </div>
      <div v-if="isLoadingAlbums" class="ui vertical stripe segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <div v-else-if="albums" class="ui vertical stripe segment">
        <h2><i18next path="Albums by this artist"/></h2>
        <div class="ui stackable doubling three column grid">
          <div class="column" :key="album.id" v-for="album in albums">
            <album-card :mode="'rich'" class="fluid" :album="album"></album-card>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
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
      isLoadingAlbums: true,
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
        self.isLoading = false
        self.isLoadingAlbums = true
        axios.get('albums/', {params: {artist: this.id, ordering: '-release_date'}}).then((response) => {
          self.albums = JSON.parse(JSON.stringify(response.data.results)).map((album) => {
            return backend.Album.clean(album)
          })

          self.isLoadingAlbums = false
        })
      })
    }
  },
  computed: {
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
<style scoped>
</style>
