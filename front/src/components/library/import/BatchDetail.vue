<template>
  <div v-title="labels.title">
    <div v-if="isLoading && !batch" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="batch" class="ui vertical stripe segment">
      <table class="ui very basic table">
        <tbody>
          <tr>
            <td>
              <strong><translate>Import batch</translate></strong>
            </td>
            <td>
              #{{ batch.id }}
            </td>
          </tr>
          <tr>
            <td>
              <strong><translate>Launch date</translate></strong>
            </td>
            <td>
              <human-date :date="batch.creation_date"></human-date>
            </td>
          </tr>
          <tr v-if="batch.user">
            <td>
              <strong><translate>Submitted by</translate></strong>
            </td>
            <td>
              <username :username="batch.user.username" />
            </td>
          </tr>
          <tr v-if="stats">
            <td><strong><translate>Pending</translate></strong></td>
            <td>{{ stats.pending }}</td>
          </tr>
          <tr v-if="stats">
            <td><strong><translate>Skipped</translate></strong></td>
            <td>{{ stats.skipped }}</td>
          </tr>
          <tr v-if="stats">
            <td><strong><translate>Errored</translate></strong></td>
            <td>
              {{ stats.errored }}
              <button
                @click="rerun({batches: [batch.id], jobs: []})"
                v-if="stats.errored > 0"
                class="ui tiny basic icon button">
                <i class="redo icon" />
                <translate>Rerun errored jobs</translate>
              </button>
            </td>
          </tr>
          <tr v-if="stats">
            <td><strong><translate>Finished</translate></strong></td>
            <td>{{ stats.finished }}/{{ stats.count}}</td>
          </tr>
        </tbody>
      </table>
      <div class="ui inline form">
        <div class="fields">
          <div class="ui field">
            <label><translate>Search</translate></label>
            <input type="text" v-model="jobFilters.search" :placeholder="labels.searchPlaceholder" />
          </div>
          <div class="ui field">
            <label><translate>Status</translate></label>
            <select class="ui dropdown" v-model="jobFilters.status">
              <option :value="null"><translate>Any</translate></option>
              <option :value="'pending'"><translate>Pending</translate></option>
              <option :value="'errored'"><translate>Errored</translate></option>
              <option :value="'finished'"><translate>Success</translate></option>
              <option :value="'skipped'"><translate>Skipped</translate></option>
            </select>
          </div>
        </div>
      </div>
      <table v-if="jobResult" class="ui unstackable table">
        <thead>
          <tr>
            <th><translate>Job ID</translate></th>
            <th><translate>Recording MusicBrainz ID</translate></th>
            <th><translate>Source</translate></th>
            <th><translate>Status</translate></th>
            <th><translate>Track</translate></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobResult.results">
            <td>{{ job.id }}</th>
            <td>
              <a :href="'https://www.musicbrainz.org/recording/' + job.mbid" target="_blank">{{ job.mbid }}</a>
            </td>
            <td>
              <a :title="job.source" :href="job.source" target="_blank">
                {{ job.source|truncate(50) }}
              </a>
            </td>
            <td>
              <span
                :class="['ui', {'yellow': job.status === 'pending'}, {'red': job.status === 'errored'}, {'green': job.status === 'finished'}, 'label']">
                {{ job.status }}</span>
                <button
                  @click="rerun({batches: [], jobs: [job.id]})"
                  v-if="job.status === 'errored'"
                  :title="labels.rerun"
                  class="ui tiny basic icon button">
                  <i class="redo icon" />
                </button>
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
              v-if="jobResult && jobResult.count > jobFilters.paginateBy"
              @page-changed="selectPage"
              :compact="true"
              :current="jobFilters.page"
              :paginate-by="jobFilters.paginateBy"
              :total="jobResult.count"
              ></pagination>
            </th>
            <th v-if="jobResult && jobResult.results.length > 0">
              <translate
                :translate-params="{start: ((jobFilters.page-1) * jobFilters.paginateBy) + 1, end: ((jobFilters.page-1) * jobFilters.paginateBy) + jobResult.results.length, total: jobResult.count}">
                Showing results %{ start }-%{ end } on %{ total }
              </translate>
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
  computed: {
    labels () {
      let msg = this.$gettext('Import Batch #%{ id }')
      let title = this.$gettextInterpolate(msg, {id: this.id})
      let rerun = this.$gettext('Rerun job')
      let searchPlaceholder = this.$gettext('Search by source...')
      return {
        title,
        searchPlaceholder,
        rerun
      }
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
        if (self.stats.pending > 0) {
          self.timeout = setTimeout(
            self.fetchStats,
            5000
          )
        }
      })
    },
    rerun ({jobs, batches}) {
      let payload = {
        jobs, batches
      }
      let self = this
      axios.post('import-jobs/run/', payload).then((response) => {
        self.fetchStats()
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
