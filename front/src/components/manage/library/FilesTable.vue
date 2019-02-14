<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label><translate :translate-context="'Content/Search/Input.Label'">Search</translate></label>
          <input name="search" type="text" v-model="search" :placeholder="labels.searchPlaceholder" />
        </div>
        <div class="field">
          <label><translate :translate-context="'Content/Search/Dropdown.Label'">Ordering</translate></label>
          <select class="ui dropdown" v-model="ordering">
            <option v-for="option in orderingOptions" :value="option[0]">
              {{ sharedLabels.filters[option[1]] }}
            </option>
          </select>
        </div>
        <div class="field">
          <label><translate :translate-context="'Content/Search/Dropdown.Label/Noun'">Order</translate></label>
          <select class="ui dropdown" v-model="orderingDirection">
            <option value="+"><translate :translate-context="'Content/Search/Dropdown'">Ascending</translate></option>
            <option value="-"><translate :translate-context="'Content/Search/Dropdown'">Descending</translate></option>
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
        :action-url="'manage/library/uploads/action/'"
        :filters="actionFilters">
        <template slot="header-cells">
          <th><translate :translate-context="'*/*/*/Short, Noun'">Title</translate></th>
          <th><translate :translate-context="'*/*/*/Short, Noun'">Artist</translate></th>
          <th><translate :translate-context="'*/*/*/Short, Noun'">Album</translate></th>
          <th><translate :translate-context="'Content/Library/Table.Label/Short, Noun'">Import date</translate></th>
          <th><translate :translate-context="'Content/Library/Table.Label/Short, Noun'">Type</translate></th>
          <th><translate :translate-context="'Content/*/*/Short, Noun'">Bitrate</translate></th>
          <th><translate :translate-context="'Content/*/*/Short, Noun'">Duration</translate></th>
          <th><translate :translate-context="'Content/*/*/Short, Noun'">Size</translate></th>
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
          <td v-if="scope.obj.mimetype">
            {{ scope.obj.mimetype }}
          </td>
          <td v-else>
            <translate :translate-context="'*/*/*'">N/A</translate>
          </td>
          <td v-if="scope.obj.bitrate">
            {{ scope.obj.bitrate | humanSize }}/s
          </td>
          <td v-else>
            <translate :translate-context="'*/*/*'">N/A</translate>
          </td>
          <td v-if="scope.obj.duration">
            {{ time.parse(scope.obj.duration) }}
          </td>
          <td v-else>
            <translate :translate-context="'*/*/*'">N/A</translate>
          </td>
          <td v-if="scope.obj.size">
            {{ scope.obj.size | humanSize }}
          </td>
          <td v-else>
            <translate :translate-context="'*/*/*'">N/A</translate>
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
        <translate :translate-context="'Content/Library/Paragraph'"
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
import Pagination from '@/components/Pagination'
import ActionTable from '@/components/common/ActionTable'
import OrderingMixin from '@/components/mixins/Ordering'
import TranslationsMixin from '@/components/mixins/Translations'

export default {
  mixins: [OrderingMixin, TranslationsMixin],
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
        ['creation_date', 'creation_date'],
        ['accessed_date', 'accessed_date'],
        ['modification_date', 'modification_date'],
        ['size', 'size'],
        ['bitrate', 'bitrate'],
        ['duration', 'duration']
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
      axios.get('/manage/library/uploads/', {params: params}).then((response) => {
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
        searchPlaceholder: this.$pgettext('Content/Search/Input.Placeholder', 'Search by title, artist, domain…')
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
      let msg = this.$pgettext('Content/Library/Dropdown/Verb', 'Delete')
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
