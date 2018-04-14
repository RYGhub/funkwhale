<template>
  <div>
    <div class="ui inline form">
      <input type="text" v-model="search" placeholder="Search by title, artist, domain..." />
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
          <th>Title</th>
          <th>Artist</th>
          <th>Album</th>
          <th>Published date</th>
          <th v-if="showLibrary">Library</th>
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
              In library
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
          <th>Showing results {{ ((page-1) * paginateBy) + 1 }}-{{ ((page-1) * paginateBy) + result.results.length }} on {{ result.count }}</th>
          <th>
            <button
              @click="launchImport"
              :disabled="checked.length === 0 || isImporting"
              :class="['ui', 'green', {loading: isImporting}, 'button']">Import {{ checked.length }} tracks
            </button>
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
      isImporting: false
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
        library_tracks: this.checked
      }
      axios.post('/submit/federation/', payload).then((response) => {
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
    }
  }
}
</script>
