<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoadingLibrary" :class="['ui', {'active': isLoadingLibrary}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading library data...</translate></div>
    </div>
    <detail-area v-else :library="library">
      <div class="ui top attached tabular menu">
        <a :class="['item', {active: currentTab === 'follows'}]" @click="currentTab = 'follows'"><translate>Followers</translate></a>
        <a :class="['item', {active: currentTab === 'tracks'}]" @click="currentTab = 'tracks'"><translate>Tracks</translate></a>
        <a :class="['item', {active: currentTab === 'edit'}]" @click="currentTab = 'edit'"><translate>Edit</translate></a>
      </div>
      <div :class="['ui', 'bottom', 'attached', 'segment', {hidden: currentTab != 'follows'}]">
        <div class="ui form">
          <div class="field">
            <label><translate>Sharing link</translate></label>
            <p><translate>Share this link with other users so they can request an access to your library.</translate></p>
            <copy-input :value="library.fid" />
          </div>
        </div>
        <div class="ui hidden divider"></div>
        <div v-if="isLoadingFollows" :class="['ui', {'active': isLoadingFollows}, 'inverted', 'dimmer']">
          <div class="ui text loader"><translate>Loading followers...</translate></div>
        </div>
        <table v-else-if="follows && follows.count > 0" class="ui table">
          <thead>
            <tr>
              <th><translate>User</translate></th>
              <th><translate>Date</translate></th>
              <th><translate>Status</translate></th>
              <th><translate>Action</translate></th>
            </tr>
          </thead>
          <tr v-for="follow in follows.results" :key="follow.fid">
            <td><actor-link :actor="follow.actor" /></td>
            <td><human-date :date="follow.creation_date" /></td>
            <td>
              <span :class="['ui', 'yellow', 'basic', 'label']" v-if="follow.approved === null">
                <translate>Pending approval</translate>
              </span>
              <span :class="['ui', 'green', 'basic', 'label']" v-else-if="follow.approved === true">
                <translate>Accepted</translate>
              </span>
              <span :class="['ui', 'red', 'basic', 'label']" v-else-if="follow.approved === false">
                <translate>Rejected</translate>
              </span>
            </td>
            <td>
              <div @click="updateApproved(follow, true)" :class="['ui', 'mini', 'icon', 'labeled', 'green', 'button']" v-if="follow.approved === null || follow.approved === false">
                <i class="ui check icon"></i> <translate>Accept</translate>
              </div>
              <div @click="updateApproved(follow, false)" :class="['ui', 'mini', 'icon', 'labeled', 'red', 'button']" v-if="follow.approved === null || follow.approved === true">
                <i class="ui x icon"></i> <translate>Reject</translate>
              </div>
            </td>
          </tr>

        </table>
        <p v-else><translate>Nobody is following this library</translate></p>
      </div>
      <div :class="['ui', 'bottom', 'attached', 'segment', {hidden: currentTab != 'tracks'}]">
        <library-files-table :filters="{library: library.uuid}"></library-files-table>
      </div>
      <div :class="['ui', 'bottom', 'attached', 'segment', {hidden: currentTab != 'edit'}]">
        <library-form :library="library" @updated="libraryUpdated" @deleted="libraryDeleted" />
      </div>
    </detail-area>
  </div>
</template>

<script>
import axios from 'axios'
import DetailMixin from './DetailMixin'
import DetailArea from './DetailArea'
import LibraryForm from './Form'
import LibraryFilesTable from './FilesTable'

export default {
  mixins: [DetailMixin],
  components: {
    DetailArea,
    LibraryForm,
    LibraryFilesTable
  },
  data () {
    return {
      currentTab: 'follows',
      isLoadingFollows: false,
      follows: null
    }
  },
  created () {
    this.fetchFollows()
  },
  methods: {
    libraryUpdated () {
      this.hiddenForm = true
      this.fetch()
    },
    libraryDeleted () {
      this.$router.push({
        name: 'content.libraries.index'
      })
    },
    fetchFollows () {
      let self = this
      self.isLoadingLibrary = true
      axios.get(`libraries/${this.id}/follows/`).then((response) => {
        self.follows = response.data
        self.isLoadingFollows = false
      })
    },
    updateApproved (follow, value) {
      let self = this
      let action
      if (value) {
        action = 'accept'
      } else {
        action = 'reject'
      }
      axios.post(`federation/follows/library/${follow.uuid}/${action}/`).then((response) => {
        follow.isLoading = false
        follow.approved = value
      })
    }
  }
}
</script>
