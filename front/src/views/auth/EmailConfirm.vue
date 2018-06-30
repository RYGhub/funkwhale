<template>
  <div class="main pusher" v-title="$gettext('Confirm your email')">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>{{ $gettext('Confirm your email') }}</h2>
        <form v-if="!success" class="ui form" @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">{{ $gettext('Error while confirming your email') }}</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label>{{ $gettext('Confirmation code') }}</label>
            <input type="text" required v-model="key" />
          </div>
          <router-link :to="{path: '/login'}">
            {{ $gettext('Back to login') }}
          </router-link>
          <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
            {{ $gettext('Confirm your email') }}</button>
        </form>
        <div v-else class="ui positive message">
          <div class="header">{{ $gettext('Email confirmed') }}</div>
          <p>{{ $gettext('Your email address was confirmed, you can now use the service without limitations.') }}</p>
          <router-link :to="{name: 'login'}">
            {{ $gettext('Proceed to login') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['defaultKey'],
  data () {
    return {
      isLoading: false,
      errors: [],
      key: this.defaultKey,
      success: false
    }
  },
  methods: {
    submit () {
      let self = this
      self.isLoading = true
      self.errors = []
      let payload = {
        key: this.key
      }
      return axios.post('auth/registration/verify-email/', payload).then(response => {
        self.isLoading = false
        self.success = true
      }, error => {
        self.errors = error.backendErrors
        self.isLoading = false
      })
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
