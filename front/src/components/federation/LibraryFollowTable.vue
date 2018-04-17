<template>
  <div>
    <div class="ui form">
      <div class="fields">
        <div class="ui six wide field">
          <input type="text" v-model="search" placeholder="Search by username, domain..." />
        </div>
        <div class="ui four wide inline field">
          <div class="ui checkbox">
            <input v-model="pending" type="checkbox">
            <label><i18next path="Pending approval"/></label>
          </div>
        </div>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <table v-if="result" class="ui very basic single line unstackable table">
      <thead>
        <tr>
          <i18next tag="th" path="Actor"/>
          <i18next tag="th" path="Creation date"/>
          <i18next tag="th" path="Status"/>
          <i18next tag="th" path="Actions"/>
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
              <i class="check icon"></i><i18next path="Approved"/>
            </template>
            <template v-else-if="follow.approved === false">
              <i class="x icon"></i><i18next path="Refused"/>
            </template>
            <template v-else>
              <i class="clock icon"></i><i18next path="Pending"/>
            </template>
          </td>
          <td>
            <dangerous-button v-if="follow.approved !== false" class="tiny basic labeled icon" color='red' @confirm="updateFollow(follow, false)">
              <i class="x icon"></i><i18next path="Deny"/>
              <p slot="modal-header"><i18next path="Deny access?"/></p>
              <p slot="modal-content">
                <i18next path="By confirming, {%0%}@{%1%} will be denied access to your library.">
                  {{ follow.actor.preferred_username }}
                  {{ follow.actor.domain }}
                </i18next>
              </p>
              <p slot="modal-confirm"><i18next path="Deny"/></p>
            </dangerous-button>
            <dangerous-button v-if="follow.approved !== true" class="tiny basic labeled icon" color='green' @confirm="updateFollow(follow, true)">
              <i class="x icon"></i> <i18next path="Approve"/>
              <p slot="modal-header"><i18next path="Approve access?"/></p>
              <p slot="modal-content">
                <i18next path="By confirming, {%0%}@{%1%} will be granted access to your library.">
                  {{ follow.actor.preferred_username }}
                  {{ follow.actor.domain }}
                </i18next>
              <p slot="modal-confirm"><i18next path="Approve"/></p>
            </dangerous-button>
          </td>
        </tr>
      </tbody>
      <tfoot class="full-width">
        <tr>
          <th>
            <pagination
            v-if="result && result.results.length > 0"
            @page-changed="selectPage"
            :compact="true"
            :current="page"
            :paginate-by="paginateBy"
            :total="result.count"
            ></pagination>
          </th>
          <th v-if="result && result.results.length > 0">
            <i18next path="Showing results {%0%}-{%1%} on {%2%}">
              {{ ((page-1) * paginateBy) + 1 }}
              {{ ((page-1) * paginateBy) + result.results.length }}
              {{ result.count }}
            </i18next>
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
