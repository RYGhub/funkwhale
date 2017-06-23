<template>
  <div class="main pusher">
    <div class="ui vertical center aligned stripe segment">
      <div :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
        <div class="ui text loader">Loading your favorites...</div>
      </div>
      <h2 v-if="results" class="ui center aligned icon header">
        <i class="circular inverted heart pink icon"></i>
        {{ favoriteTracks.count }} favorites
      </h2>
      <radio-button type="favorites"></radio-button>

    </div>
    <div class="ui vertical stripe segment">
      <button class="ui left floated labeled icon button" @click="fetchFavorites(previousLink)" :disabled="!previousLink"><i class="left arrow icon"></i> Previous</button>
      <button class="ui right floated right labeled icon button" @click="fetchFavorites(nextLink)" :disabled="!nextLink">Next <i class="right arrow icon"></i></button>
      <div class="ui hidden clearing divider"></div>
      <div class="ui hidden clearing divider"></div>
      <track-table v-if="results" :tracks="results.results"></track-table>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import logger from '@/logging'
import config from '@/config'
import favoriteTracks from '@/favorites/tracks'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'

const FAVORITES_URL = config.API_URL + 'tracks/'

export default {
  components: {
    TrackTable,
    RadioButton
  },
  data () {
    return {
      results: null,
      isLoading: false,
      nextLink: null,
      previousLink: null,
      favoriteTracks
    }
  },
  created () {
    this.fetchFavorites(FAVORITES_URL)
  },
  methods: {
    fetchFavorites (url) {
      var self = this
      this.isLoading = true
      let params = {
        favorites: 'true'
      }
      logger.default.time('Loading user favorites')
      this.$http.get(url, {params: params}).then((response) => {
        self.results = response.data
        self.nextLink = response.data.next
        self.previousLink = response.data.previous
        Vue.set(favoriteTracks, 'count', response.data.count)
        favoriteTracks.count = response.data.count
        self.results.results.forEach((track) => {
          Vue.set(favoriteTracks.objects, track.id, true)
        })
        logger.default.timeEnd('Loading user favorites')
        self.isLoading = false
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
