<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui six wide field">
          <label><translate>Search</translate></label>
          <input type="text" v-model="search" :placeholder="labels.searchPlaceholder" />
        </div>
        <div class="ui field">
          <label><translate>Import status</translate></label>
          <select class="ui dropdown" v-model="importedFilter">
            <option :value="null"><translate>Any</translate></option>
            <option :value="'imported'"><translate>Imported</translate></option>
            <option :value="'not_imported'"><translate>Not imported</translate></option>
            <option :value="'import_pending'"><translate>Import pending</translate></option>
          </select>
        </div>
        <div class="field">
          <label><translate>Ordering</translate></label>
          <select class="ui dropdown" v-model="ordering">
            <option v-for="option in orderingOptions" :value="option[0]">
              {{ option[1] }}
            </option>
          </select>
        </div>
        <div class="field">
          <label><translate>Ordering direction</translate></label>
          <select class="ui dropdown" v-model="orderingDirection">
            <option value="+"><translate>Ascending</translate></option>
            <option value="-"><translate>Descending</translate></option>
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
          <th><translate>Status</translate></th>
          <th><translate>Title</translate></th>
          <th><translate>Artist</translate></th>
          <th><translate>Album</translate></th>
          <th><translate>Published date</translate></th>
          <th v-if="showLibrary"><translate>Library</translate></th>
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
            <span v-if="scope.obj.status === 'imported'" class="ui basic green label"><translate>In library</translate></span>
            <span v-else-if="scope.obj.status === 'import_pending'" class="ui basic yellow label"><translate>Import pending</translate></span>
            <span v-else class="ui basic label"><translate>Not imported</translate></span>
          </td>
          <td>
            <span :title="scope.obj.title">{{ scope.obj.title|truncate(30) }}</span>
          </td>
          <td>
            <span class="discrete link" @click="updateSearch({key: 'artist', value: scope.obj.artist_name})" :title="scope.obj.artist_name">{{ scope.obj.artist_name|truncate(30) }}</span>
          </td>
          <td>
            <span class="discrete link" @click="updateSearch({key: 'album', value: scope.obj.album_title})" :title="scope.obj.album_title">{{ scope.obj.album_title|truncate(20) }}</span>
          </td>
          <td>
            <human-date :date="scope.obj.published_date"></human-date>
          </td>
          <td v-if="showLibrary">
            <span class="discrete link" @click="updateSearch({key: 'domain', value: scope.obj.library.actor.domain})">{{ scope.obj.library.actor.domain }}</span>
          </td>
        </template>
      </action-table>
    </div>
    <div>
      <pagination
        v-if="result && result.count > paginateBy"
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
import OrderingMixin from '@/components/mixins/Ordering'

export default {
  mixins: [OrderingMixin],
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
      importedFilter: null,
      orderingDirection: '-',
      ordering: 'published_date',
      orderingOptions: [
        ['published_date', 'Published date'],
        ['title', 'Title'],
        ['album_title', 'Album title'],
        ['artist_name', 'Artist name']
      ]
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    updateSearch ({key, value}) {
      if (value.indexOf(' ') > -1) {
        value = `"${value}"`
      }
      this.search = `${key}:${value}`
    },
    fetchData () {
      let params = _.merge({
        'page': this.page,
        'page_size': this.paginateBy,
        'ordering': this.getOrderingAsString(),
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
    labels () {
      return {
        searchPlaceholder: this.$gettext('Search by title, artist, domain...')
      }
    },
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
    orderingDirection: function () {
      this.page = 1
      this.fetchData()
    },
    ordering: function () {
      this.page = 1
      this.fetchData()
    },
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
