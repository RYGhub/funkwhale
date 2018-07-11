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
          <th><translate>Username</translate></th>
          <th><translate>Email</translate></th>
          <th><translate>Account status</translate></th>
          <th><translate>Sign-up</translate></th>
          <th><translate>Last activity</translate></th>
          <th><translate>Permissions</translate></th>
          <th><translate>Status</translate></th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            <router-link :to="{name: 'manage.users.users.detail', params: {id: scope.obj.id }}">{{ scope.obj.username }}</router-link>
          </td>
          <td>
            <span>{{ scope.obj.email }}</span>
          </td>
          <td>
            <span v-if="scope.obj.is_active" class="ui basic green label"><translate>Active</translate></span>
            <span v-else class="ui basic grey label"><translate>Inactive</translate></span>
          </td>
          <td>
            <human-date :date="scope.obj.date_joined"></human-date>
          </td>
          <td>
            <human-date v-if="scope.obj.last_activity" :date="scope.obj.last_activity"></human-date>
            <template v-else><translate>N/A</translate></template>
          </td>
          <td>
            <template v-for="p in permissions">
              <span class="ui basic tiny label" v-if="scope.obj.permissions[p.code]">{{ p.label }}</span>
            </template>
          </td>
          <td>
            <span v-if="scope.obj.is_superuser" class="ui pink label"><translate>Admin</translate></span>
            <span v-else-if="scope.obj.is_staff" class="ui purple label"><translate>Staff member</translate></span>
            <span v-else class="ui basic label"><translate>regular user</translate></span>
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
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || '-date_joined')
    return {
      time,
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 50,
      search: '',
      orderingDirection: defaultOrdering.direction || '+',
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['date_joined', 'Sign-up date'],
        ['last_activity', 'Last activity'],
        ['username', 'Username']
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
      axios.get('/manage/users/users/', {params: params}).then((response) => {
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
        searchPlaceholder: this.$gettext('Search by username, email, name...')
      }
    },
    privacyLevels () {
      return {}
    },
    permissions () {
      return [
        {
          'code': 'upload',
          'label': this.$gettext('Upload')
        },
        {
          'code': 'library',
          'label': this.$gettext('Library')
        },
        {
          'code': 'federation',
          'label': this.$gettext('Federation')
        },
        {
          'code': 'settings',
          'label': this.$gettext('Settings')
        }
      ]
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
      return [
        // {
        //   name: 'delete',
        //   label: this.$gettext('Delete'),
        //   isDangerous: true
        // }
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
