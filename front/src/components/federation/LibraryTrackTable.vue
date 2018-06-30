<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label>{{ $gettext('Search') }}</label>
          <input type="text" v-model="search" placeholder="Search by title, artist, domain..." />
        </div>
        <div class="ui field">
          <label>{{ $gettext('Import status') }}</label>
          <select class="ui dropdown" v-model="importedFilter">
            <option :value="null">{{ $gettext('Any') }}</option>
            <option :value="'imported'">{{ $gettext('Imported') }}</option>
            <option :value="'not_imported'">{{ $gettext('Not imported') }}</option>
            <option :value="'import_pending'">{{ $gettext('Import pending') }}</option>
          </select>
        </div>
      </div>
    </div>
    <div class="dimmable">
      <div v-if="isLoading" class="ui active inverted dimmer">
          <div class="ui loader"></div>
      </div>
      <action-table
        v-if="result"
        @action-launched="fetchData"
        :objects-data="result"
        :actions="actions"
        :action-url="'federation/library-tracks/action/'"
        :filters="actionFilters">
        <template slot="header-cells">
          <th>{{ $gettext('Status') }}</th>
          <th>{{ $gettext('Title') }}</th>
          <th>{{ $gettext('Artist') }}</th>
          <th>{{ $gettext('Album') }}</th>
          <th>{{ $gettext('Published date') }}</th>
          <th v-if="showLibrary">{{ $gettext('Library') }}</th>
        </template>
        <template slot="action-success-footer" slot-scope="scope">
          <router-link
            v-if="scope.result.action === 'import'"
            :to="{name: 'library.import.batches.detail', params: {id: scope.result.result.batch.id }}">
            <translate
              :translate-params="{id: scope.result.result.batch.id}">
              Import #%{ id } launched
            </translate>
          </router-link>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            <span v-if="scope.obj.status === 'imported'" class="ui basic green label">{{ $gettext('In library') }}</span>
            <span v-else-if="scope.obj.status === 'import_pending'" class="ui basic yellow label">{{ $gettext('Import pending') }}</span>
            <span v-else class="ui basic label">{{ $gettext('Not imported') }}</span>
          </td>
          <td>
            <span :title="scope.obj.title">{{ scope.obj.title|truncate(30) }}</span>
          </td>
          <td>
            <span :title="scope.obj.artist_name">{{ scope.obj.artist_name|truncate(30) }}</span>
          </td>
          <td>
            <span :title="scope.obj.album_title">{{ scope.obj.album_title|truncate(20) }}</span>
          </td>
          <td>
            <human-date :date="scope.obj.published_date"></human-date>
          </td>
          <td v-if="showLibrary">
            {{ scope.obj.library.actor.domain }}
          </td>
        </template>
      </action-table>
    </div>
    <div>
      <pagination
        v-if="result && result.results.length > 0"
        @page-changed="selectPage"
        :compact="true"
        :current="page"
        :paginate-by="paginateBy"
        :total="result.count"
        ></pagination>

      <span v-if="result && result.results.length > 0">
        <translate
          :translate-params="{start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count}">
          Showing results %{ start }-%{ end } on %{ total }
        </translate>
      </span>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'

import Pagination from '@/components/Pagination'
import ActionTable from '@/components/common/ActionTable'

export default {
  props: {
    filters: {type: Object, required: false},
    showLibrary: {type: Boolean, default: false}
  },
  components: {
    Pagination,
    ActionTable
  },
  data () {
    return {
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 25,
      search: '',
      importedFilter: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      let params = _.merge({
        'page': this.page,
        'page_size': this.paginateBy,
        'q': this.search
      }, this.filters)
      if (this.importedFilter !== null) {
        params.status = this.importedFilter
      }
      let self = this
      self.isLoading = true
      self.checked = []
      axios.get('/federation/library-tracks/', {params: params}).then((response) => {
        self.result = response.data
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    selectPage: function (page) {
      this.page = page
    }
  },
  computed: {
    actionFilters () {
      var currentFilters = {
        q: this.search
      }
      if (this.filters) {
        return _.merge(currentFilters, this.filters)
      } else {
        return currentFilters
      }
    },
    actions () {
      let msg = this.$gettext('Import')
      return [
        {
          name: 'import',
          label: msg,
          filterCheckable: (obj) => { return obj.status === 'not_imported' }
        }
      ]
    }
  },
  watch: {
    search (newValue) {
      this.page = 1
      this.fetchData()
    },
    page () {
      this.fetchData()
    },
    importedFilter () {
      this.page = 1
      this.fetchData()
    }
  }
}
</script>
