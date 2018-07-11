<template>
  <div v-title="labels.title">
    <div class="ui vertical stripe segment">
      <div v-if="isLoading" :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      <div class="ui inline form">
        <div class="fields">
          <div class="ui field">
            <label><translate>Search</translate></label>
            <input type="text" v-model="filters.search" :placeholder="labels.searchPlaceholder" />
          </div>
          <div class="ui field">
            <label><translate>Status</translate></label>
            <select class="ui dropdown" v-model="filters.status">
              <option :value="null"><translate>Any</translate></option>
              <option :value="'pending'"><translate>Pending</translate></option>
              <option :value="'errored'"><translate>Errored</translate></option>
              <option :value="'finished'"><translate>Success</translate></option>
            </select>
          </div>
          <div class="ui field">
            <label><translate>Import source</translate></label>
            <select class="ui dropdown" v-model="filters.source">
              <option :value="null"><translate>Any</translate></option>
              <option :value="'shell'"><translate>CLI</translate></option>
              <option :value="'api'"><translate>API</translate></option>
              <option :value="'federation'"><translate>Federation</translate></option>
            </select>
          </div>
        </div>
      </div>
      <div class="ui hidden clearing divider"></div>
      <table v-if="result && result.results.length > 0" class="ui unstackable table">
        <thead>
          <tr>
            <th><translate>ID</translate></th>
            <th><translate>Launch date</translate></th>
            <th><translate>Jobs</translate></th>
            <th><translate>Status</translate></th>
            <th><translate>Source</translate></th>
            <th><translate>Submitted by</translate></th>
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
              v-if="result && result.count > filters.paginateBy"
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
  computed: {
    labels () {
      let searchPlaceholder = this.$gettext('Search by submitter, source...')
      let title = this.$gettext('Import Batches')
      return {
        searchPlaceholder,
        title
      }
    }
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
