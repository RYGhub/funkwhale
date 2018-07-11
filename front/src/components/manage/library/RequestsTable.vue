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
        <div class="field">
          <label><translate>Status</translate></label>
          <select class="ui dropdown" v-model="status">
            <option :value="null"><translate>All</translate></option>
            <option :value="'pending'"><translate>Pending</translate></option>
            <option :value="'accepted'"><translate>Accepted</translate></option>
            <option :value="'imported'"><translate>Imported</translate></option>
            <option :value="'closed'"><translate>Closed</translate></option>
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
          <th><translate>User</translate></th>
          <th><translate>Status</translate></th>
          <th><translate>Artist</translate></th>
          <th><translate>Albums</translate></th>
          <th><translate>Comment</translate></th>
          <th><translate>Creation date</translate></th>
          <th><translate>Import date</translate></th>
          <th><translate>Actions</translate></th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            {{ scope.obj.user.username }}
          </td>
          <td>
            <span class="ui green basic label" v-if="scope.obj.status === 'imported'"><translate>Imported</translate></span>
            <span class="ui pink basic label" v-else-if="scope.obj.status === 'accepted'"><translate>Accepted</translate></span>
            <span class="ui yellow basic label" v-else-if="scope.obj.status === 'pending'"><translate>Pending</translate></span>
            <span class="ui red basic label" v-else-if="scope.obj.status === 'closed'"><translate>Closed</translate></span>
          </td>
          <td>
            <span :title="scope.obj.artist_name">{{ scope.obj.artist_name|truncate(30) }}</span>
          </td>
          <td>
            <span v-if="scope.obj.albums" :title="scope.obj.albums">{{ scope.obj.albums|truncate(30) }}</span>
            <template v-else><translate>N/A</translate></template>
          </td>
          <td>
            <span v-if="scope.obj.comment" :title="scope.obj.comment">{{ scope.obj.comment|truncate(30) }}</span>
            <template v-else><translate>N/A</translate></template>
          </td>
          <td>
            <human-date :date="scope.obj.creation_date"></human-date>
          </td>
          <td>
            <human-date v-if="scope.obj.imported_date" :date="scope.obj.creation_date"></human-date>
            <template v-else><translate>N/A</translate></template>
          </td>
          <td>
            <router-link
              class="ui tiny basic button"
              :to="{name: 'library.import.launch', query: {request: scope.obj.id}}"
              v-if="scope.obj.status === 'pending'"><translate>Create import</translate></router-link>
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
    labels () {
      return {
        searchPlaceholder: this.$gettext('Search by artist, username, comment...')
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
      // somehow, extraction fails otherwise
      let deleteLabel = this.$gettext('Delete')
      let markImportedLabel = this.$gettext('Mark as imported')
      let markClosedLabel = this.$gettext('Mark as closed')
      return [
        {
          name: 'delete',
          label: deleteLabel,
          isDangerous: true
        },
        {
          name: 'mark_imported',
          label: markImportedLabel,
          filterCheckable: (obj) => { return ['pending', 'accepted'].indexOf(obj.status) > -1 },
          isDangerous: true
        },
        {
          name: 'mark_closed',
          label: markClosedLabel,
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
