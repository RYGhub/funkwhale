<template>
  <div class="ui card">
    <div class="content">
      <div class="header">
        {{ libraryData.display_name }}
      </div>
    </div>
    <div class="content">
      <span class="right floated" v-if="libraryData.actor.manuallyApprovesFollowers">
        <i class="lock icon"></i> Followers only
      </span>
      <span>
        <i class="music icon"></i>
        {{ libraryData.library.totalItems }} tracks
      </span>
    </div>
    <div class="extra content">
      <template v-if="libraryData.local.awaiting_approval">
        <i class="clock icon"></i>
        Follow request pending approval
      </template>
      <template v-else-if="libraryData.local.following">Pending follow request
        <i class="check icon"></i>
        Already following this library
      </template>
      <div
        v-else-if="!library"
        @click="follow"
        :disabled="isLoading"
        :class="['ui', 'basic', {loading: isLoading}, 'green', 'button']">
        <template v-if="libraryData.actor.manuallyApprovesFollowers">
          Send a follow request
        </template>
        <template v-else>
          Follow
        </template>
      </div>
      <router-link
        v-else
        class="ui basic button"
        :to="{name: 'federation.libraries.detail', params: {id: library.uuid }}">
        Detail
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['libraryData'],
  data () {
    return {
      isLoading: false,
      data: null,
      errors: [],
      library: null
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
  }
}
</script>
