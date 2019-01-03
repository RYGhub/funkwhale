<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui six wide field">
          <label><translate>Search</translate></label>
          <form @submit.prevent="search.query = $refs.search.value">
            <input ref="search" type="text" :value="search.query" :placeholder="labels.searchPlaceholder" />
          </form>
        </div>
        <div class="field">
          <label><translate>Import status</translate></label>
          <select class="ui dropdown" @change="addSearchToken('status', $event.target.value)" :value="getTokenValue('status', '')">
            <option value=""><translate>All</translate></option>
            <option value="pending"><translate>Pending</translate></option>
            <option value="skipped"><translate>Skipped</translate></option>
            <option value="errored"><translate>Errored</translate></option>
            <option value="finished"><translate>Finished</translate></option>
          </select>
        </div>
        <div class="field">
          <label><translate>Ordering</translate></label>
          <select class="ui dropdown" v-model="ordering">
            <option v-for="option in orderingOptions" :value="option[0]">
              {{ sharedLabels.filters[option[1]] }}
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
        :id-field="'uuid'"
        :objects-data="result"
        :custom-objects="customObjects"
        :actions="actions"
        :refreshable="true"
        :needs-refresh="needsRefresh"
        :action-url="'uploads/action/'"
        @refresh="fetchData"
        :filters="actionFilters">
        <template slot="header-cells">
          <th><translate>Title</translate></th>
          <th><translate>Artist</translate></th>
          <th><translate>Album</translate></th>
          <th><translate>Upload date</translate></th>
          <th><translate>Import status</translate></th>
          <th><translate>Duration</translate></th>
          <th><translate>Size</translate></th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <template v-if="scope.obj.track">
            <td>
              <span :title="scope.obj.track.title">{{ scope.obj.track.title|truncate(25) }}</span>
            </td>
            <td>
              <span class="discrete link" @click="addSearchToken('artist', scope.obj.track.artist.name)" :title="scope.obj.track.artist.name">{{ scope.obj.track.artist.name|truncate(20) }}</span>
            </td>
            <td>
              <span class="discrete link" @click="addSearchToken('album', scope.obj.track.album.title)" :title="scope.obj.track.album.title">{{ scope.obj.track.album.title|truncate(20) }}</span>
            </td>
          </template>
          <template v-else>
            <td>{{ scope.obj.source }}</td>
            <td></td>
            <td></td>
          </template>
          <td>
            <human-date :date="scope.obj.creation_date"></human-date>
          </td>
          <td :title="labels.importStatuses[scope.obj.import_status].help">
            <span class="discrete link" @click="addSearchToken('status', scope.obj.import_status)">
              {{ labels.importStatuses[scope.obj.import_status].label }}
              <i class="question circle outline icon"></i>
            </span>
          </td>
          <td v-if="scope.obj.duration">
            {{ time.parse(scope.obj.duration) }}
          </td>
          <td v-else>
            <translate>N/A</translate>
          </td>
          <td v-if="scope.obj.size">
            {{ scope.obj.size | humanSize }}
          </td>
          <td v-else>
            <translate>N/A</translate>
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
import _ from '@/lodash'
import time from '@/utils/time'
import {normalizeQuery, parseTokens} from '@/search'

import Pagination from '@/components/Pagination'
import ActionTable from '@/components/common/ActionTable'
import OrderingMixin from '@/components/mixins/Ordering'
import TranslationsMixin from '@/components/mixins/Translations'
import SmartSearchMixin from '@/components/mixins/SmartSearch'

export default {
  mixins: [OrderingMixin, TranslationsMixin, SmartSearchMixin],
  props: {
    filters: {type: Object, required: false},
    needsRefresh: {type: Boolean, required: false, default: false},
    customObjects: {type: Array, required: false, default: () => { return [] }}
  },
  components: {
    Pagination,
    ActionTable
  },
  data () {
    return {
      time,
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 25,
      search: {
        query: this.defaultQuery,
        tokens: parseTokens(normalizeQuery(this.defaultQuery))
      },
      orderingDirection: '-',
      ordering: 'creation_date',
      orderingOptions: [
        ['creation_date', 'creation_date'],
        ['title', 'title'],
        ['size', 'size'],
        ['duration', 'duration'],
        ['bitrate', 'bitrate'],
        ['album_title', 'album_title'],
        ['artist_name', 'artist_name']
      ]
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.$emit('fetch-start')
      let params = _.merge({
        'page': this.page,
        'page_size': this.paginateBy,
        'ordering': this.getOrderingAsString(),
        'q': this.search.query
      }, this.filters || {})
      let self = this
      self.isLoading = true
      self.checked = []
      axios.get('/uploads/', {params: params}).then((response) => {
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
        searchPlaceholder: this.$gettext('Search by title, artist, album...'),
        importStatuses: {
          skipped: {
            label: this.$gettext('Skipped'),
            help: this.$gettext('Track was already present in one of your libraries'),
          },
          pending: {
            label: this.$gettext('Pending'),
            help: this.$gettext('Track is uploaded but not processed by the server yet'),
          },
          errored: {
            label: this.$gettext('Errored'),
            help: this.$gettext('An error occured while processing this track, ensure the track is correctly tagged'),
          },
          finished: {
            label: this.$gettext('Finished'),
            help: this.$gettext('Import went on successfully'),
          },
        }
      }
    },
    actionFilters () {
      var currentFilters = {
        q: this.search.query
      }
      if (this.filters) {
        return _.merge(currentFilters, this.filters)
      } else {
        return currentFilters
      }
    },
    actions () {
      let deleteMsg = this.$gettext('Delete')
      let relaunchMsg = this.$gettext('Relaunch import')
      return [
        {
          name: 'delete',
          label: deleteMsg,
          isDangerous: true,
          allowAll: true
        },
        {
          name: 'relaunch_import',
          label: relaunchMsg,
          isDangerous: true,
          allowAll: true,
          filterCheckable: f => {
            return f.import_status != 'finished'
          }
        }
      ]
    }
  },
  watch: {
    orderingDirection: function () {
      this.page = 1
      this.fetchData()
    },
    page: function () {
      this.fetchData()
    },
    ordering: function () {
      this.page = 1
      this.fetchData()
    },
    search (newValue) {
      this.page = 1
      this.fetchData()
    }
  }
}
</script>
