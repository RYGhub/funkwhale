<template>
  <div>
    <div class="ui form">
      <div class="fields">
        <div class="ui six wide field">
          <input type="text" v-model="search" :placeholder="labels.searchPlaceholder" />
        </div>
        <div class="ui four wide inline field">
          <div class="ui checkbox">
            <input v-model="pending" type="checkbox">
            <label>
              <translate>Pending approval</translate>
            </label>
          </div>
        </div>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <table v-if="result" class="ui very basic single line unstackable table">
      <thead>
        <tr>
          <th><translate>Actor</translate></th>
          <th><translate>Creation date</translate></th>
          <th><translate>Status</translate></th>
          <th><translate>Actions</translate></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="follow in result.results">
          <td>
            {{ follow.actor.preferred_username }}@{{ follow.actor.domain }}
          </td>
          <td>
            <human-date :date="follow.creation_date"></human-date>
          </td>
          <td>
            <template v-if="follow.approved === true">
              <i class="check icon"></i>
              <translate>Approved</translate>
            </template>
            <template v-else-if="follow.approved === false">
              <i class="x icon"></i>
              <translate>Refused</translate>
            </template>
            <template v-else>
              <i class="clock icon"></i>
              <translate>Pending</translate>
            </template>
          </td>
          <td>
            <dangerous-button v-if="follow.approved !== false" class="tiny basic labeled icon" color='red' @confirm="updateFollow(follow, false)">
              <i class="x icon"></i>
              <translate>Deny</translate>
              <p slot="modal-header">
                <translate>Deny access?</translate>
              </p>
              <p slot="modal-content">
                <translate
                  :translate-params="{username: follow.actor.preferred_username + '@' + follow.actor.domain}">
                  By confirming, %{ username } will be denied access to your library.
                </translate>
              </p>
              <p slot="modal-confirm">
                <translate>Deny</translate>
              </p>
            </dangerous-button>
            <dangerous-button v-if="follow.approved !== true" class="tiny basic labeled icon" color='green' @confirm="updateFollow(follow, true)">
              <i class="check icon"></i>
              <translate>Approve</translate>
              <p slot="modal-header">
                <translate>Approve access?</translate>
              </p>
              <p slot="modal-content">
                <translate
                  :translate-params="{username: follow.actor.preferred_username + '@' + follow.actor.domain}">
                  By confirming, %{ username } will be granted access to your library.
                </translate>
              <p slot="modal-confirm">
                <translate>Approve</translate>
              </p>
            </dangerous-button>
          </td>
        </tr>
      </tbody>
      <tfoot class="full-width">
        <tr>
          <th>
            <pagination
            v-if="result && result.count > paginateBy"
            @page-changed="selectPage"
            :compact="true"
            :current="page"
            :paginate-by="paginateBy"
            :total="result.count"
            ></pagination>
          </th>
          <th v-if="result && result.results.length > 0">
            <translate
              :translate-params="{start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count}">
              Showing results %{ start }-%{ end } on %{ total }
            </translate>
          </th>
          <th></th>
          <th></th>
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
    filters: {type: Object, required: false, default: () => {}}
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
      pending: false
    }
  },
  created () {
    this.fetchData()
  },
  computed: {
    labels () {
      return {
        searchPlaceholder: this.$gettext('Search by username, domain...')
      }
    }
  },
  methods: {
    fetchData () {
      let params = _.merge({
        'page': this.page,
        'page_size': this.paginateBy,
        'q': this.search
      }, this.filters)
      if (this.pending) {
        params.pending = true
      }
      let self = this
      self.isLoading = true
      axios.get('/federation/libraries/followers/', {params: params}).then((response) => {
        self.result = response.data
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    selectPage: function (page) {
      this.page = page
    },
    updateFollow (follow, approved) {
      let payload = {
        follow: follow.id,
        approved: approved
      }
      let self = this
      axios.patch('/federation/libraries/followers/', payload).then((response) => {
        follow.approved = response.data.approved
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
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
    },
    pending () {
      this.fetchData()
    }
  }
}
</script>
