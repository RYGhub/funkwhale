<template>
  <div>
    <h2>Search for some music</h2>
    <div :class="['ui', {'loading': isLoading }, 'search']">
      <div class="ui icon big input">
        <i class="search icon"></i>
        <input ref="search" class="prompt" placeholder="Artist, album, track..." v-model.trim="query" type="text" />
      </div>
    </div>
    <template v-if="query.length > 0">
      <h3 class="ui title">Artists</h3>
      <div v-if="results.artists.length > 0" class="ui stackable three column grid">
        <div class="column" :key="artist.id" v-for="artist in results.artists">
          <artist-card class="fluid" :artist="artist" ></artist-card>
        </div>
      </div>
      <p v-else>Sorry, we did not found any artist matching your query</p>
    </template>
    <template v-if="query.length > 0">
      <h3 class="ui title">Albums</h3>
      <div v-if="results.albums.length > 0" class="ui stackable three column grid">
        <div class="column" :key="album.id" v-for="album in results.albums">
          <album-card class="fluid" :album="album" ></album-card>
        </div>
      </div>
      <p v-else>Sorry, we did not found any album matching your query</p>
    </template>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'
import backend from '@/audio/backend'
import AlbumCard from '@/components/audio/album/Card'
import ArtistCard from '@/components/audio/artist/Card'

export default {
  components: {
    AlbumCard,
    ArtistCard
  },
  props: {
    autofocus: {type: Boolean, default: false}
  },
  data () {
    return {
      query: '',
      results: {
        albums: [],
        artists: []
      },
      backend: backend,
      isLoading: false
    }
  },
  mounted () {
    if (this.autofocus) {
      this.$refs.search.focus()
    }
    this.search()
  },
  methods: {
    search () {
      if (this.query.length < 1) {
        return
      }
      var self = this
      self.isLoading = true
      logger.default.debug('Searching track matching "' + this.query + '"')
      let params = {
        query: this.query
      }
      axios.get('search', {
        params: params
      }).then((response) => {
        self.results = self.castResults(response.data)
        self.isLoading = false
      })
    },
    castResults (results) {
      return {
        albums: results.albums.map((album) => {
          return backend.Album.clean(album)
        }),
        artists: results.artists.map((artist) => {
          return backend.Artist.clean(artist)
        })
      }
    }
  },
  watch: {
    query () {
      this.search()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
