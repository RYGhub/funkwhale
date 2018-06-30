<template>
  <div v-title="'Import Batches'">
    <div class="ui vertical stripe segment">
      <div v-if="isLoading" :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      <div class="ui inline form">
        <div class="fields">
          <div class="ui field">
            <label>{{ $gettext('Search') }}</label>
            <input type="text" v-model="filters.search" placeholder="Search by submitter, source..." />
          </div>
          <div class="ui field">
            <label>{{ $gettext('Status') }}</label>
            <select class="ui dropdown" v-model="filters.status">
              <option :value="null">{{ $gettext('Any') }}</option>
              <option :value="'pending'">{{ $gettext('Pending') }}</option>
              <option :value="'errored'">{{ $gettext('Errored') }}</option>
              <option :value="'finished'">{{ $gettext('Success') }}</option>
            </select>
          </div>
          <div class="ui field">
            <label>{{ $gettext('Import source') }}</label>
            <select class="ui dropdown" v-model="filters.source">
              <option :value="null">{{ $gettext('Any') }}</option>
              <option :value="'shell'">{{ $gettext('CLI') }}</option>
              <option :value="'api'">{{ $gettext('API') }}</option>
              <option :value="'federation'">{{ $gettext('Federation') }}</option>
            </select>
          </div>
        </div>
      </div>
      <div class="ui hidden clearing divider"></div>
      <table v-if="result && result.results.length > 0" class="ui unstackable table">
        <thead>
          <tr>
            <th>{{ $gettext('ID') }}</th>
            <th>{{ $gettext('Launch date') }}</th>
            <th>{{ $gettext('Jobs') }}</th>
            <th>{{ $gettext('Status') }}</th>
            <th>{{ $gettext('Source') }}</th>
            <th>{{ $gettext('Submitted by') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="obj in result.results">
            <td>{{ obj.id }}</th>
            <td>
              <router-link :to="{name: 'library.import.batches.detail', params: {id: obj.id }}">
                <human-date :date="obj.creation_date"></human-date>
              </router-link>
            </td>
            <td>{{ obj.job_count }}</td>
            <td>
              <span
                :class="['ui', {'yellow': obj.status === 'pending'}, {'red': obj.status === 'errored'}, {'green': obj.status === 'finished'}, 'label']">{{ obj.status }}
              </span>
            </td>
            <td>{{ obj.source }}</td>
            <td><template v-if="obj.submitted_by">{{ obj.submitted_by.username }}</template></td>
          </tr>
        </tbody>
        <tfoot class="full-width">
          <tr>
            <th>
              <pagination
              v-if="result && result.results.length > 0"
              @page-changed="selectPage"
              :compact="true"
              :current="filters.page"
              :paginate-by="filters.paginateBy"
              :total="result.count"
              ></pagination>
            </th>
            <th v-if="result && result.results.length > 0">
              <translate
                :translate-params="{start: ((filters.page-1) * filters.paginateBy) + 1, end: ((filters.page-1) * filters.paginateBy) + result.results.length, total: result.count}">
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
import axios from 'axios'
import logger from '@/logging'
import Pagination from '@/components/Pagination'

export default {
  components: {
    Pagination
  },
  data () {
    return {
      result: null,
      isLoading: false,
      filters: {
        status: null,
        source: null,
        search: '',
        paginateBy: 25,
        page: 1
      }
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      let params = {
        page_size: this.filters.paginateBy,
        page: this.filters.page,
        q: this.filters.search
      }
      if (this.filters.status) {
        params.status = this.filters.status
      }
      if (this.filters.source) {
        params.source = this.filters.source
      }
      var self = this
      this.isLoading = true
      logger.default.time('Loading import batches')
      axios.get('import-batches/', {params}).then((response) => {
        self.result = response.data
        logger.default.timeEnd('Loading import batches')
        self.isLoading = false
      })
    },
    selectPage: function (page) {
      this.filters.page = page
    }
  },
  watch: {
    filters: {
      handler () {
        this.fetchData()
      },
      deep: true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
