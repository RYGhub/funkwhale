<template>
  <div v-title="'Import Batch #' + id">
    <div v-if="isLoading && !batch" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="batch" class="ui vertical stripe segment">
      <table class="ui very basic table">
        <tbody>
          <tr>
            <td>
              <strong>{{ $t('Import batch') }}</strong>
            </td>
            <td>
              #{{ batch.id }}
            </td>
          </tr>
          <tr>
            <td>
              <strong>{{ $t('Launch date') }}</strong>
            </td>
            <td>
              <human-date :date="batch.creation_date"></human-date>
            </td>
          </tr>
          <tr v-if="batch.user">
            <td>
              <strong>{{ $t('Submitted by') }}</strong>
            </td>
            <td>
              <username :username="batch.user.username" />
            </td>
          </tr>
          <tr v-if="stats">
            <td><strong>{{ $t('Pending') }}</strong></td>
            <td>{{ stats.pending }}</td>
          </tr>
          <tr v-if="stats">
            <td><strong>{{ $t('Skipped') }}</strong></td>
            <td>{{ stats.skipped }}</td>
          </tr>
          <tr v-if="stats">
            <td><strong>{{ $t('Errored') }}</strong></td>
            <td>{{ stats.errored }}</td>
          </tr>
          <tr v-if="stats">
            <td><strong>{{ $t('Finished') }}</strong></td>
            <td>{{ stats.finished }}/{{ stats.count}}</td>
          </tr>
        </tbody>
      </table>
      <div class="ui inline form">
        <div class="fields">
          <div class="ui field">
            <label>{{ $t('Search') }}</label>
            <input type="text" v-model="jobFilters.search" placeholder="Search by source..." />
          </div>
          <div class="ui field">
            <label>{{ $t('Status') }}</label>
            <select class="ui dropdown" v-model="jobFilters.status">
              <option :value="null">{{ $t('Any') }}</option>
              <option :value="'pending'">{{ $t('Pending') }}</option>
              <option :value="'errored'">{{ $t('Errored') }}</option>
              <option :value="'finished'">{{ $t('Success') }}</option>
              <option :value="'skipped'">{{ $t('Skipped') }}</option>
            </select>
          </div>
        </div>
      </div>
      <table v-if="jobResult" class="ui unstackable table">
        <thead>
          <tr>
            <th>{{ $t('Job ID') }}</th>
            <th>{{ $t('Recording MusicBrainz ID') }}</th>
            <th>{{ $t('Source') }}</th>
            <th>{{ $t('Status') }}</th>
            <th>{{ $t('Track') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobResult.results">
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
        <tfoot class="full-width">
          <tr>
            <th>
              <pagination
              v-if="jobResult && jobResult.results.length > 0"
              @page-changed="selectPage"
              :compact="true"
              :current="jobFilters.page"
              :paginate-by="jobFilters.paginateBy"
              :total="jobResult.count"
              ></pagination>
            </th>
            <th v-if="jobResult && jobResult.results.length > 0">
              {{ $t('Showing results {%start%}-{%end%} on {%total%}', {start: ((jobFilters.page-1) * jobFilters.paginateBy) + 1 , end: ((jobFilters.page-1) * jobFilters.paginateBy) + jobResult.results.length, total: jobResult.count})}}
            <th>
            <th></th>
            <th></th>
            <th></th>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import logger from '@/logging'
import Pagination from '@/components/Pagination'

export default {
  props: ['id'],
  components: {
    Pagination
  },
  data () {
    return {
      isLoading: true,
      batch: null,
      stats: null,
      jobResult: null,
      timeout: null,
      jobFilters: {
        status: null,
        source: null,
        search: '',
        paginateBy: 25,
        page: 1
      }
    }
  },
  created () {
    let self = this
    this.fetchData().then(() => {
      self.fetchJobs()
      self.fetchStats()
    })
  },
  destroyed () {
    if (this.timeout) {
      clearTimeout(this.timeout)
    }
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      let url = 'import-batches/' + this.id + '/'
      logger.default.debug('Fetching batch "' + this.id + '"')
      return axios.get(url).then((response) => {
        self.batch = response.data
        self.isLoading = false
        if (self.batch.status === 'pending') {
          self.timeout = setTimeout(
            self.fetchData,
            5000
          )
        }
      })
    },
    fetchStats () {
      var self = this
      let url = 'import-jobs/stats/'
      axios.get(url, {params: {batch: self.id}}).then((response) => {
        let old = self.stats
        self.stats = response.data
        self.isLoading = false
        if (!_.isEqual(old, self.stats)) {
          self.fetchJobs()
          self.fetchData()
        }
        if (self.batch.status === 'pending') {
          self.timeout = setTimeout(
            self.fetchStats,
            5000
          )
        }
      })
    },
    fetchJobs () {
      let params = {
        batch: this.id,
        page_size: this.jobFilters.paginateBy,
        page: this.jobFilters.page,
        q: this.jobFilters.search
      }
      if (this.jobFilters.status) {
        params.status = this.jobFilters.status
      }
      if (this.jobFilters.source) {
        params.source = this.jobFilters.source
      }
      let self = this
      axios.get('import-jobs/', {params}).then((response) => {
        self.jobResult = response.data
      })
    },
    selectPage: function (page) {
      this.jobFilters.page = page
    }

  },
  watch: {
    id () {
      this.fetchData()
    },
    jobFilters: {
      handler () {
        this.fetchJobs()
      },
      deep: true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
