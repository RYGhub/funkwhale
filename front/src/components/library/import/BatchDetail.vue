<template>
  <div>
    <div v-if="isLoading && !batch" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="batch" class="ui vertical stripe segment">
      <div :class="
        ['ui',
        {'active': batch.status === 'pending'},
        {'warning': batch.status === 'pending'},
        {'error': batch.status === 'errored'},
        {'success': batch.status === 'finished'},
        'progress']">
        <div class="bar" :style="progressBarStyle">
          <div class="progress"></div>
        </div>
        <div v-if="batch.status === 'pending'" class="label">Importing {{ batch.jobs.length }} tracks...</div>
        <div v-if="batch.status === 'finished'" class="label">Imported {{ batch.jobs.length }} tracks!</div>
      </div>
      <table class="ui table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Recording MusicBrainz ID</th>
            <th>Source</th>
            <th>Status</th>
            <th>Track</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in batch.jobs">
            <td>{{ job.id }}</th>
            <td>
              <a :href="'https://www.musicbrainz.org/recording/' + job.mbid" target="_blank">{{ job.mbid }}</a>
            </td>
            <td>
              <a :href="job.source" target="_blank">{{ job.source }}</a>
            </td>
            <td>
              <span
                :class="['ui', {'yellow': job.status === 'pending'}, {'red': job.status === 'errored'}, {'green': job.status === 'finished'}, 'label']">{{ job.status }}</span>
            </td>
            <td>
              <router-link v-if="job.track_file" :to="{name: 'library.tracks.detail', params: {id: job.track_file.track }}">{{ job.track_file.track }}</router-link>
            </td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<script>

import logger from '@/logging'
import config from '@/config'

const FETCH_URL = config.API_URL + 'import-batches/'

export default {
  props: ['id'],
  data () {
    return {
      isLoading: true,
      batch: null
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
      logger.default.debug('Fetching batch "' + this.id + '"')
      this.$http.get(url).then((response) => {
        self.batch = response.data
        self.isLoading = false
        if (self.batch.status === 'pending') {
          setTimeout(
            self.fetchData,
            5000
          )
        }
      })
    }
  },
  computed: {
    progress () {
      return this.batch.jobs.filter(j => {
        return j.status !== 'pending'
      }).length * 100 / this.batch.jobs.length
    },
    progressBarStyle () {
      return 'width: ' + parseInt(this.progress) + '%'
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
