<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui field">
          <label>{{ $t('Search') }}</label>
          <input type="text" v-model="search" placeholder="Search by username, email, name..." />
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
            <option value="+">{{ $t('Ascending') }}</option>
            <option value="-">{{ $t('Descending') }}</option>
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
          <th>{{ $t('Username') }}</th>
          <th>{{ $t('Email') }}</th>
          <th>{{ $t('Account status') }}</th>
          <th>{{ $t('Sign-up') }}</th>
          <th>{{ $t('Last activity') }}</th>
          <th>{{ $t('Permissions') }}</th>
          <th>{{ $t('Status') }}</th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <td>
            <router-link :to="{name: 'manage.users.users.detail', params: {id: scope.obj.id }}">{{ scope.obj.username }}</router-link>
          </td>
          <td>
            <span>{{ scope.obj.email }}</span>
          </td>
          <td>
            <span v-if="scope.obj.is_active" class="ui basic green label">{{ $t('Active') }}</span>
            <span v-else class="ui basic grey label">{{ $t('Inactive') }}</span>
          </td>
          <td>
            <human-date :date="scope.obj.date_joined"></human-date>
          </td>
          <td>
            <human-date v-if="scope.obj.last_activity" :date="scope.obj.last_activity"></human-date>
            <template v-else>{{ $t('N/A') }}</template>
          </td>
          <td>
            <template v-for="p in permissions">
              <span class="ui basic tiny label" v-if="scope.obj.permissions[p.code]">{{ p.label }}</span>
            </template>
          </td>
          <td>
            <span v-if="scope.obj.is_superuser" class="ui pink label">{{ $t('Admin') }}</span>
            <span v-else-if="scope.obj.is_staff" class="ui purple label">{{ $t('Staff member') }}</span>
            <span v-else class="ui basic label">{{ $t('regular user') }}</span>
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
    privacyLevels () {
      return {}
    },
    permissions () {
      return [
        {
          'code': 'upload',
          'label': this.$t('Upload')
        },
        {
          'code': 'library',
          'label': this.$t('Library')
        },
        {
          'code': 'federation',
          'label': this.$t('Federation')
        },
        {
          'code': 'settings',
          'label': this.$t('Settings')
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
        //   label: this.$t('Delete'),
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
