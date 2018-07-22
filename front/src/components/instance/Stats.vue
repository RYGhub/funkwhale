<template>
  <div>
    <div v-if="stats" class="ui stackable two column grid">
      <div class="column">
        <h3 class="ui left aligned header">
          <translate>User activity</translate>
        </h3>
        <div v-if="stats" class="ui mini horizontal statistics">
          <div class="statistic">
            <div class="value">
              <i class="green user icon"></i>
              {{ stats.users }}
            </div>
            <div class="label"><translate>users</translate></div>
          </div>
          <div class="statistic">
            <div class="value">
              <i class="orange sound icon"></i> {{ stats.listenings }}
            </div>
            <div class="label"><translate>tracks listened</translate></div>
          </div>
          <div class="statistic">
            <div class="value">
              <i class="pink heart icon"></i> {{ stats.trackFavorites }}
            </div>
            <div class="label"><translate>Tracks favorited</translate></div>
          </div>
        </div>
      </div>
      <div class="column">
        <h3 class="ui left aligned header"><translate>Library</translate></h3>
        <div class="ui mini horizontal statistics">
          <div class="statistic">
            <div class="value">
              {{ parseInt(stats.musicDuration) }}
            </div>
            <div class="label"><translate>Hours of music</translate></div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.artists }}
            </div>
            <div class="label"><translate>Artists</translate></div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.albums }}
            </div>
            <div class="label"><translate>Albums</translate></div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.tracks }}
            </div>
            <div class="label"><translate>tracks</translate></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import logger from '@/logging'

export default {
  data () {
    return {
      stats: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      logger.default.debug('Fetching instance stats...')
      axios.get('instance/nodeinfo/2.0/').then((response) => {
        let d = response.data
        self.stats = {}
        self.stats.users = _.get(d, 'usage.users.total')
        self.stats.listenings = _.get(d, 'metadata.usage.listenings.total')
        self.stats.trackFavorites = _.get(d, 'metadata.usage.favorites.tracks.total')
        self.stats.musicDuration = _.get(d, 'metadata.library.music.hours')
        self.stats.artists = _.get(d, 'metadata.library.artists.total')
        self.stats.albums = _.get(d, 'metadata.library.albums.total')
        self.stats.tracks = _.get(d, 'metadata.library.tracks.total')
        self.isLoading = false
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
