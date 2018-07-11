<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label><translate>Search</translate></label>
          <input type="text" v-model="search" :placeholder="labels.searchPlaceholder" />
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
        :action-url="'manage/library/track-files/action/'"
        :filters="actionFilters">
        <template slot="header-cells">
          <th><translate>Title</translate></th>
          <th><translate>Artist</translate></th>
          <th><translate>Album</translate></th>
          <th><translate>Import date</translate></th>
          <th><translate>Type</translate></th>
          <th><translate>Bitrate</translate></th>
          <th><translate>Duration</translate></th>
          <th><translate>Size</translate></th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            <span :title="scope.obj.track.title">{{ scope.obj.track.title|truncate(30) }}</span>
          </td>
          <td>
            <span :title="scope.obj.track.artist.name">{{ scope.obj.track.artist.name|truncate(30) }}</span>
          </td>
          <td>
            <span :title="scope.obj.track.album.title">{{ scope.obj.track.album.title|truncate(20) }}</span>
          </td>
          <td>
            <human-date :date="scope.obj.creation_date"></human-date>
          </td>
          <td v-if="scope.obj.audio_mimetype">
            {{ scope.obj.audio_mimetype }}
          </td>
          <td v-else>
            <translate>N/A</translate>
          </td>
          <td v-if="scope.obj.bitrate">
            {{ scope.obj.bitrate | humanSize }}/s
          </td>
          <td v-else>
            <translate>N/A</translate>
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
import _ from 'lodash'
import time from '@/utils/time'
import Pagination from '@/components/Pagination'
import ActionTable from '@/components/common/ActionTable'
import OrderingMixin from '@/components/mixins/Ordering'

export default {
  mixins: [OrderingMixin],
  props: {
    filters: {type: Object, required: false}
  },
  components: {
    Pagination,
    ActionTable
  },
  data () {
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || '-creation_date')
    return {
      time,
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 25,
      search: '',
      orderingDirection: defaultOrdering.direction || '+',
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['creation_date', 'Creation date'],
        ['accessed_date', 'Accessed date'],
        ['modification_date', 'Modification date'],
        ['size', 'Size'],
        ['bitrate', 'Bitrate'],
        ['duration', 'Duration']
      ]

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
        'q': this.search,
        'ordering': this.getOrderingAsString()
      }, this.filters)
      let self = this
      self.isLoading = true
      self.checked = []
      axios.get('/manage/library/track-files/', {params: params}).then((response) => {
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
      let msg = this.$gettext('Delete')
      return [
        {
          name: 'delete',
          label: msg,
          isDangerous: true
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
    ordering () {
      this.fetchData()
    },
    orderingDirection () {
      this.fetchData()
    }
  }
}
</script>
