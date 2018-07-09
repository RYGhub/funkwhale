<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="labels.title">
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
                <translate
                  tag="div"
                  translate-plural="%{ count } tracks in %{ albumsCount } albums"
                  :translate-n="totalTracks"
                  :translate-params="{count: totalTracks, albumsCount: totalAlbums}">
                  %{ count } track in %{ albumsCount } albums
                </translate>
              </div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <radio-button type="artist" :object-id="artist.id"></radio-button>
          <play-button class="orange" :artist="artist.id">
            <translate>Play all albums</translate>
          </play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <translate>Search on Wikipedia</translate>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <translate>View on MusicBrainz</translate>
          </a>
        </div>
      </div>
      <div v-if="isLoadingAlbums" class="ui vertical stripe segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <div v-else-if="albums && albums.length > 0" class="ui vertical stripe segment">
        <h2>
          <translate>Albums by this artist</translate>
        </h2>
        <div class="ui stackable doubling three column grid">
          <div class="column" :key="album.id" v-for="album in albums">
            <album-card :mode="'rich'" class="fluid" :album="album"></album-card>
          </div>
        </div>
      </div>
      <div v-if="tracks.length > 0" class="ui vertical stripe segment">
        <h2>
          <translate>Tracks by this artist</translate>
        </h2>
        <track-table :display-position="true" :tracks="tracks"></track-table>
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
import TrackTable from '@/components/audio/track/Table'

export default {
  props: ['id'],
  components: {
    AlbumCard,
    RadioButton,
    PlayButton,
    TrackTable
  },
  data () {
    return {
      isLoading: true,
      isLoadingAlbums: true,
      artist: null,
      albums: null,
      tracks: []
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      logger.default.debug('Fetching artist "' + this.id + '"')
      axios.get('tracks/', {params: {artist: this.id}}).then((response) => {
        self.tracks = response.data.results
      })
      axios.get('artists/' + this.id + '/').then((response) => {
        self.artist = response.data
        self.isLoading = false
        self.isLoadingAlbums = true
        axios.get('albums/', {params: {artist: this.id, ordering: '-release_date'}}).then((response) => {
          let parsed = JSON.parse(JSON.stringify(response.data.results))
          self.albums = parsed.map((album) => {
            return backend.Album.clean(album)
          })

          self.isLoadingAlbums = false
        })
      })
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Artist')
      }
    },
    totalAlbums () {
      let trackAlbums = _.uniqBy(this.tracks, (t) => {
        return t.album.id
      })
      return this.albums.length + trackAlbums.length
    },
    totalTracks () {
      if (this.albums.length === 0) {
        return 0 + this.tracks.length
      }
      return this.albums.map((album) => {
        return album.tracks.length
      }).reduce((a, b) => {
        return a + b
      }) + this.tracks.length
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
