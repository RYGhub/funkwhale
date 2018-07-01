<template>
  <div v-title="labels.title">
    <div class="ui vertical stripe segment">
      <search :autofocus="true"></search>
    </div>
    <div class="ui vertical stripe segment">
      <div class="ui stackable three column grid">
        <div class="column">
          <h2 class="ui header">
            <translate>Latest artists</translate>
          </h2>
          <div :class="['ui', {'active': isLoadingArtists}, 'inline', 'loader']"></div>
          <div v-if="artists.length > 0" v-for="artist in artists.slice(0, 3)" :key="artist.id" class="ui cards">
            <artist-card :artist="artist"></artist-card>
          </div>
        </div>
        <div class="column">
          <h2 class="ui header">
            <translate>Radios</translate>
          </h2>
          <radio-card :type="'favorites'"></radio-card>
          <radio-card :type="'random'"></radio-card>
          <radio-card :type="'less-listened'"></radio-card>
        </div>
        <div class="column">
          <h2 class="ui header">
            <translate>Music requests</translate>
          </h2>
          <request-form v-if="$store.state.auth.authenticated"></request-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Search from '@/components/audio/Search'
import logger from '@/logging'
import ArtistCard from '@/components/audio/artist/Card'
import RadioCard from '@/components/radios/Card'
import RequestForm from '@/components/requests/Form'

const ARTISTS_URL = 'artists/'

export default {
  name: 'library',
  components: {
    Search,
    ArtistCard,
    RadioCard,
    RequestForm
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
  computed: {
    labels () {
      return {
        title: this.$gettext('Home')
      }
    }
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
