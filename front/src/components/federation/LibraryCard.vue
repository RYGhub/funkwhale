<template>
  <div class="ui card">
    <div class="content">
      <div class="header ellipsis">
        <router-link
          v-if="library"
          :title="displayName"
          :to="{name: 'federation.libraries.detail', params: {id: library.uuid }}">
          {{ displayName }}
        </router-link>
        <span :title="displayName" v-else>{{ displayName }}</span>
      </div>
    </div>
    <div class="content">
      <span class="right floated" v-if="following">
        <i class="check icon"></i><translate>Following</translate>
      </span>
      <span class="right floated" v-else-if="manuallyApprovesFollowers">
        <i class="lock icon"></i><translate>Followers only</translate>
      </span>
      <span class="right floated" v-else>
        <i class="open lock icon"></i><translate>Open</translate>
      </span>
      <span v-if="totalItems">
        <i class="music icon"></i>
        <translate
          translate-plural="%{ count } tracks"
          :translate-n="totalItems"
          :translate-params="{count: totalItems}">
          1 track
        </translate>
      </span>
    </div>
    <div class="extra content">
      <template v-if="awaitingApproval">
        <i class="clock icon"></i>
        <translate>Follow request pending approval</translate>
      </template>
      <div
        v-if="!library"
        @click="follow"
        :disabled="isLoading"
        :class="['ui', 'basic', {loading: isLoading}, 'green', 'button']">
        <translate v-if="manuallyApprovesFollowers">Send a follow request</translate>
        <translate v-else>Follow</translate>
      </div>
      <router-link
        v-else
        class="ui basic button"
        :to="{name: 'federation.libraries.detail', params: {id: library.uuid }}">
        <translate>Detail</translate>
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['libraryData', 'libraryInstance'],
  data () {
    return {
      library: this.libraryInstance,
      isLoading: false,
      data: null,
      errors: []
    }
  },
  methods: {
    follow () {
      let params = {
        'actor': this.libraryData['actor']['id'],
        'autoimport': false,
        'download_files': false,
        'federation_enabled': true
      }
      let self = this
      self.isLoading = true
      axios.post('/federation/libraries/', params).then((response) => {
        self.$emit('follow', {data: self.libraryData, library: response.data})
        self.library = response.data
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    displayName () {
      if (this.libraryData) {
        return this.libraryData.display_name
      } else {
        return `${this.library.actor.preferred_username}@${this.library.actor.domain}`
      }
    },
    manuallyApprovesFollowers () {
      if (this.libraryData) {
        return this.libraryData.actor.manuallyApprovesFollowers
      } else {
        return this.library.actor.manually_approves_followers
      }
    },
    totalItems () {
      if (this.libraryData) {
        return this.libraryData.library.totalItems
      } else {
        return this.library.tracks_count
      }
    },
    awaitingApproval () {
      if (this.libraryData) {
        return this.libraryData.local.awaiting_approval
      } else {
        return this.library.follow.approved === null
      }
    },
    following () {
      if (this.libraryData) {
        return this.libraryData.local.following
      } else {
        return this.library.follow.approved
      }
    }
  }
}
</script>
