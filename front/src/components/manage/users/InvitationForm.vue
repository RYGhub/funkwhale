<template>
  <div>
    <form class="ui form" @submit.prevent="submit">
      <div v-if="errors.length > 0" class="ui negative message">
        <div class="header">{{ $t('Error while creating invitation') }}</div>
        <ul class="list">
          <li v-for="error in errors">{{ error }}</li>
        </ul>
      </div>
      <div class="inline fields">
        <div class="ui field">
          <label>{{ $t('Invitation code')}}</label>
          <input type="text" v-model="code" :placeholder="$t('Leave empty for a random code')" />
        </div>
        <div class="ui field">
          <button :class="['ui', {loading: isLoading}, 'button']" :disabled="isLoading" type="submit">
            {{ $t('Get a new invitation') }}
          </button>
        </div>
      </div>
    </form>
    <div v-if="invitations.length > 0">
      <div class="ui hidden divider"></div>
      <table class="ui ui basic table">
        <thead>
          <tr>
            <th>{{ $t('Code') }}</th>
            <th>{{ $t('Share link') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invitation in invitations" :key="invitation.code">
            <td>{{ invitation.code.toUpperCase() }}</td>
            <td><a :href="getUrl(invitation.code)" target="_blank">{{ getUrl(invitation.code) }}</a></td>
          </tr>
        </tbody>
      </table>
      <button class="ui basic button" @click="invitations = []">{{ $t('Clear') }}</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

import backend from '@/audio/backend'

export default {
  data () {
    return {
      isLoading: false,
      code: null,
      invitations: [],
      errors: []
    }
  },
  methods: {
    submit () {
      let self = this
      this.isLoading = true
      this.errors = []
      let url = 'manage/users/invitations/'
      let payload = {
        code: this.code
      }
      axios.post(url, payload).then((response) => {
        self.isLoading = false
        self.invitations.unshift(response.data)
      }, (error) => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    getUrl (code) {
      return backend.absoluteUrl(this.$router.resolve({name: 'signup', query: {invitation: code.toUpperCase()}}).href)
    }
  }
}
</script>

<style scoped>
</style>
