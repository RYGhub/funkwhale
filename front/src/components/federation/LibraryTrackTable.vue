<template>
  <div>
    <div class="ui inline form">
      <input type="text" v-model="search" placeholder="Search by title, artist, domain..." />
    </div>
    <table v-if="result" class="ui compact very basic single line unstackable table">
      <thead>
        <tr>
          <th colspan="1">
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
            {{ track.title }}
          </td>
          <td>
            {{ track.artist_name }}
          </td>
          <td>
            {{ track.album_title }}
          </td>
          <td>
            <human-date :date="track.published_date"></human-date>
          </td>
        </tr>
      </tbody>
      <tfoot class="full-width">
        <tr>
          <th colspan="5">
            <button
              @click="launchImport"
              :disabled="checked.length === 0 || isImporting"
              :class="['ui', 'green', {loading: isImporting}, 'button']">Import {{ checked.length }} tracks
            </button>
          </th>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'

export default {
  props: ['filters'],
  data () {
    return {
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 50,
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
        'paginate_by': this.paginateBy,
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
        console.log('Triggered import', response.data)
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
        this.checked = this.result.results.map(t => { return t.id })
      }
    },
    toggleCheck (id) {
      if (this.checked.indexOf(id) > -1) {
        // we uncheck
        this.checked.splice(this.checked.indexOf(id), 1)
      } else {
        this.checked.push(id)
      }
    }
  },
  watch: {
    search (newValue) {
      if (newValue.length > 0) {
        this.fetchData()
      }
    }
  }
}
</script>
