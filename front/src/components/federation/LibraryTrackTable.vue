<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label>{{ $t('Search') }}</label>
          <input type="text" v-model="search" placeholder="Search by title, artist, domain..." />
        </div>
        <div class="ui field">
          <label>{{ $t('Import status') }}</label>
          <select class="ui dropdown" v-model="importedFilter">
            <option :value="null">{{ $t('Any') }}</option>
            <option :value="true">{{ $t('Imported') }}</option>
            <option :value="false">{{ $t('Not imported') }}</option>
          </select>
        </div>
      </div>
    </div>
    <table v-if="result" class="ui compact very basic single line unstackable table">
      <thead>
        <tr>
          <th>
            <div class="ui checkbox">
              <input
                type="checkbox"
                @change="toggleCheckAll"
                :checked="result.results.length === checked.length"><label>&nbsp;</label>
            </div>
          </th>
          <i18next tag="th" path="Title"/>
          <i18next tag="th" path="Artist"/>
          <i18next tag="th" path="Album"/>
          <i18next tag="th" path="Published date"/>
          <i18next tag="th" v-if="showLibrary" path="Library"/>
        </tr>
      </thead>
      <tbody>
        <tr v-for="track in result.results">
          <td class="collapsing">
            <div v-if="!track.local_track_file" class="ui checkbox">
              <input
                type="checkbox"
                @change="toggleCheck(track.id)"
                :checked="checked.indexOf(track.id) > -1"><label>&nbsp;</label>
            </div>
            <div v-else class="ui label">
              <i18next path="In library"/>
            </div>
          </td>
          <td>
            <span :title="track.title">{{ track.title|truncate(30) }}</span>
          </td>
          <td>
            <span :title="track.artist_name">{{ track.artist_name|truncate(30) }}</span>
          </td>
          <td>
            <span :title="track.album_title">{{ track.album_title|truncate(20) }}</span>
          </td>
          <td>
            <human-date :date="track.published_date"></human-date>
          </td>
          <td v-if="showLibrary">
            {{ track.library.actor.domain }}
          </td>
        </tr>
      </tbody>
      <tfoot class="full-width">
        <tr>
          <th>
            <pagination
            v-if="result && result.results.length > 0"
            @page-changed="selectPage"
            :compact="true"
            :current="page"
            :paginate-by="paginateBy"
            :total="result.count"
            ></pagination>

          </th>
          <th v-if="result && result.results.length > 0">
            {{ $t('Showing results {%start%}-{%end%} on {%total%}', {start: ((page-1) * paginateBy) + 1 , end: ((page-1) * paginateBy) + result.results.length, total: result.count})}}
          <th>
            <button
              @click="launchImport"
              :disabled="checked.length === 0 || isImporting"
              :class="['ui', 'green', {loading: isImporting}, 'button']">
              {{ $t('Import {%count%} tracks', {'count': checked.length}) }}
            </button>
            <router-link
              v-if="importBatch"
              :to="{name: 'library.import.batches.detail', params: {id: importBatch.id }}">
              {{ $t('Import #{% id %} launched', {id: importBatch.id}) }}
            </router-link>
          </th>
          <th></th>
          <th></th>
          <th></th>
          <th v-if="showLibrary"></th>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'

import Pagination from '@/components/Pagination'

export default {
  props: {
    filters: {type: Object, required: false},
    showLibrary: {type: Boolean, default: false}
  },
  components: {
    Pagination
  },
  data () {
    return {
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 25,
      search: '',
      checked: {},
      isImporting: false,
      importBatch: null,
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
        params.imported = this.importedFilter
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
    launchImport () {
      let self = this
      self.isImporting = true
      let payload = {
        objects: this.checked,
        action: 'import'
      }
      axios.post('/federation/library-tracks/action/', payload).then((response) => {
        self.importBatch = response.data.result.batch
        self.isImporting = false
        self.fetchData()
      }, error => {
        self.isImporting = false
        self.errors = error.backendErrors
      })
    },
    toggleCheckAll () {
      if (this.checked.length === this.result.results.length) {
        // we uncheck
        this.checked = []
      } else {
        this.checked = this.result.results.filter(t => {
          return t.local_track_file === null
        }).map(t => { return t.id })
      }
    },
    toggleCheck (id) {
      if (this.checked.indexOf(id) > -1) {
        // we uncheck
        this.checked.splice(this.checked.indexOf(id), 1)
      } else {
        this.checked.push(id)
      }
    },
    selectPage: function (page) {
      this.page = page
    }
  },
  watch: {
    search (newValue) {
      if (newValue.length > 0) {
        this.fetchData()
      }
    },
    page () {
      this.fetchData()
    },
    importedFilter () {
      this.fetchData()
    }
  }
}
</script>
