<template>
  <div>
    <div v-if="stats" class="ui stackable two column grid">
      <div class="column">
        <h3 class="ui left aligned header">User activity</h3>
        <div class="ui mini horizontal statistics">
          <div class="statistic">
            <div class="value">
              <i class="green user icon"></i>
              {{ stats.users }}
            </div>
            <div class="label">
              Users
            </div>
          </div>
          <div class="statistic">
            <div class="value">
              <i class="orange sound icon"></i> {{ stats.listenings }}
            </div>
            <div class="label">
              tracks listened
            </div>
          </div>
          <div class="statistic">
            <div class="value">
              <i class="pink heart icon"></i> {{ stats.track_favorites }}
            </div>
            <div class="label">
              Tracks favorited
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <h3 class="ui left aligned header">Library</h3>
        <div class="ui mini horizontal statistics">
          <div class="statistic">
            <div class="value">
              {{ parseInt(stats.music_duration) }}
            </div>
            <div class="label">
              hours of music
            </div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.artists }}
            </div>
            <div class="label">
              Artists
            </div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.albums }}
            </div>
            <div class="label">
              Albums
            </div>
          </div>
          <div class="statistic">
            <div class="value">
              {{ stats.tracks }}
            </div>
            <div class="label">
              tracks
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
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
      axios.get('instance/stats/').then((response) => {
        self.stats = response.data
        self.isLoading = false
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
