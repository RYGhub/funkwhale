<template>
  <div class="main pusher">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>Change my password</h2>
        <form class="ui form" @submit.prevent="submit()">
          <div v-if="error" class="ui negative message">
            <div class="header">Cannot change your password</div>
            <ul class="list">
              <li v-if="error == 'invalid_credentials'">Please double-check your password is correct</li>
            </ul>
          </div>
          <div class="field">
            <label>Old password</label>
            <input
            required
            type="password"
            autofocus
            placeholder="Enter your old password"
            v-model="old_password">
          </div>
          <div class="field">
            <label>New password</label>
            <input
            required
            type="password"
            autofocus
            placeholder="Enter your new password"
            v-model="new_password">
          </div>
          <button :class="['ui', {'loading': isLoading}, 'button']" type="submit">Change password</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'

export default {
  data () {
    return {
      // We need to initialize the component with any
      // properties that will be used in it
      old_password: '',
      new_password: '',
      error: '',
      isLoading: false
    }
  },
  methods: {
    submit () {
      var self = this
      self.isLoading = true
      this.error = ''
      var credentials = {
        old_password: this.old_password,
        new_password1: this.new_password,
        new_password2: this.new_password
      }
      let resource = Vue.resource(config.BACKEND_URL + 'api/auth/registration/change-password/')
      return resource.save({}, credentials).then(response => {
        logger.default.info('Password successfully changed')
        self.$router.push('/profile/me')
      }, response => {
        if (response.status === 400) {
          self.error = 'invalid_credentials'
        } else {
          self.error = 'unknown_error'
        }
        self.isLoading = false
      })
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
