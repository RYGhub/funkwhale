<template>
  <div>
    <div class="ui vertical stripe segment">
      <search :autofocus="true"></search>
    </div>
    <div class="ui vertical stripe segment">
      <div class="ui stackable two column grid">
        <div class="column">
          <h2 class="ui header">Latest artists</h2>
          <div :class="['ui', {'active': isLoadingArtists}, 'inline', 'loader']"></div>
          <div v-if="artists.length > 0" v-for="artist in artists.slice(0, 3)" :key="artist.id" class="ui cards">
            <artist-card :artist="artist"></artist-card>
          </div>
        </div>
        <div class="column">
          <h2 class="ui header">Radios</h2>
          <radio-card :type="'favorites'"></radio-card>
          <radio-card :type="'random'"></radio-card>
          <radio-card :type="'less-listened'"></radio-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Search from '@/components/audio/Search'
import backend from '@/audio/backend'
import logger from '@/logging'
import ArtistCard from '@/components/audio/artist/Card'
import RadioCard from '@/components/radios/Card'

const ARTISTS_URL = 'artists/'

export default {
  name: 'library',
  components: {
    Search,
    ArtistCard,
    RadioCard
  },
  data () {
    return {
      artists: [],
      isLoadingArtists: false
    }
  },
  created () {
    this.fetchArtists()
  },
  methods: {
    fetchArtists () {
      var self = this
      this.isLoadingArtists = true
      let params = {
        ordering: '-creation_date'
      }
      let url = ARTISTS_URL
      logger.default.time('Loading latest artists')
      axios.get(url, {params: params}).then((response) => {
        self.artists = response.data.results
        self.artists.map((artist) => {
          var albums = JSON.parse(JSON.stringify(artist.albums)).map((album) => {
            return backend.Album.clean(album)
          })
          artist.albums = albums
          return artist
        })
        logger.default.timeEnd('Loading latest artists')
        self.isLoadingArtists = false
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
