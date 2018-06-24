<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label>{{ $t('Search') }}</label>
          <input type="text" v-model="search" placeholder="Search by artist, username, comment..." />
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
        <div class="field">
          <label>{{ $t("Status") }}</label>
          <select class="ui dropdown" v-model="status">
            <option :value="null">{{ $t('All') }}</option>
            <option :value="'pending'">{{ $t('Pending') }}</option>
            <option :value="'accepted'">{{ $t('Accepted') }}</option>
            <option :value="'imported'">{{ $t('Imported') }}</option>
            <option :value="'closed'">{{ $t('Closed') }}</option>
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
        :action-url="'manage/requests/import-requests/action/'"
        :filters="actionFilters">
        <template slot="header-cells">
          <th>{{ $t('User') }}</th>
          <th>{{ $t('Status') }}</th>
          <th>{{ $t('Artist') }}</th>
          <th>{{ $t('Albums') }}</th>
          <th>{{ $t('Comment') }}</th>
          <th>{{ $t('Creation date') }}</th>
          <th>{{ $t('Import date') }}</th>
          <th>{{ $t('Actions') }}</th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            {{ scope.obj.user.username }}
          </td>
          <td>
            <span class="ui green basic label" v-if="scope.obj.status === 'imported'">{{ $t('Imported') }}</span>
            <span class="ui pink basic label" v-else-if="scope.obj.status === 'accepted'">{{ $t('Accepted') }}</span>
            <span class="ui yellow basic label" v-else-if="scope.obj.status === 'pending'">{{ $t('Pending') }}</span>
            <span class="ui red basic label" v-else-if="scope.obj.status === 'closed'">{{ $t('Closed') }}</span>
          </td>
          <td>
            <span :title="scope.obj.artist_name">{{ scope.obj.artist_name|truncate(30) }}</span>
          </td>
          <td>
            <span v-if="scope.obj.albums" :title="scope.obj.albums">{{ scope.obj.albums|truncate(30) }}</span>
            <template v-else>{{ $t('N/A') }}</template>
          </td>
          <td>
            <span v-if="scope.obj.comment" :title="scope.obj.comment">{{ scope.obj.comment|truncate(30) }}</span>
            <template v-else>{{ $t('N/A') }}</template>
          </td>
          <td>
            <human-date :date="scope.obj.creation_date"></human-date>
          </td>
          <td>
            <human-date v-if="scope.obj.imported_date" :date="scope.obj.creation_date"></human-date>
            <template v-else>{{ $t('N/A') }}</template>
          </td>
          <td>
            <router-link
              class="ui tiny basic button"
              :to="{name: 'library.import.launch', query: {request: scope.obj.id}}"
              v-if="scope.obj.status === 'pending'">{{ $t('Create import') }}</router-link>
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
      status: null,
      orderingDirection: defaultOrdering.direction || '+',
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['creation_date', 'Creation date'],
        ['imported_date', 'Imported date']
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
        'status': this.status,
        'ordering': this.getOrderingAsString()
      }, this.filters)
      let self = this
      self.isLoading = true
      self.checked = []
      axios.get('/manage/requests/import-requests/', {params: params}).then((response) => {
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
        },
        {
          name: 'mark_imported',
          label: this.$t('Mark as imported'),
          filterCheckable: (obj) => { return ['pending', 'accepted'].indexOf(obj.status) > -1 },
          isDangerous: true
        },
        {
          name: 'mark_closed',
          label: this.$t('Mark as closed'),
          filterCheckable: (obj) => { return ['pending', 'accepted'].indexOf(obj.status) > -1 },
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
      this.page = 1
      this.fetchData()
    },
    status () {
      this.page = 1
      this.fetchData()
    },
    orderingDirection () {
      this.page = 1
      this.fetchData()
    }
  }
}
</script>
