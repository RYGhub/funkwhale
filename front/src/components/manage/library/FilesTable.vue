<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label>{{ $t('Search') }}</label>
          <input type="text" v-model="search" placeholder="Search by title, artist, domain..." />
        </div>
        <div class="field">
          <i18next tag="label" path="Ordering"/>
          <select class="ui dropdown" v-model="ordering">
            <option v-for="option in orderingOptions" :value="option[0]">
              {{ option[1] }}
            </option>
          </select>
        </div>
        <div class="field">
          <i18next tag="label" path="Ordering direction"/>
          <select class="ui dropdown" v-model="orderingDirection">
            <option value="+">Ascending</option>
            <option value="-">Descending</option>
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
          <th>{{ $t('Title') }}</th>
          <th>{{ $t('Artist') }}</th>
          <th>{{ $t('Album') }}</th>
          <th>{{ $t('Import date') }}</th>
          <th>{{ $t('Type') }}</th>
          <th>{{ $t('Bitrate') }}</th>
          <th>{{ $t('Duration') }}</th>
          <th>{{ $t('Size') }}</th>
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
            {{ $t('N/A') }}
          </td>
          <td v-if="scope.obj.bitrate">
            {{ scope.obj.bitrate | humanSize }}/s
          </td>
          <td v-else>
            {{ $t('N/A') }}
          </td>
          <td v-if="scope.obj.duration">
            {{ time.parse(scope.obj.duration) }}
          </td>
          <td v-else>
            {{ $t('N/A') }}
          </td>
          <td v-if="scope.obj.size">
            {{ scope.obj.size | humanSize }}
          </td>
          <td v-else>
            {{ $t('N/A') }}
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
        {{ $t('Showing results {%start%}-{%end%} on {%total%}', {start: ((page-1) * paginateBy) + 1 , end: ((page-1) * paginateBy) + result.results.length, total: result.count})}}
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
      return [
        {
          name: 'delete',
          label: this.$t('Delete'),
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
