<template>
  <div class="main pusher" v-title="$gettext('Confirm your email')">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><translate>Confirm your email</translate></h2>
        <form v-if="!success" class="ui form" @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header"><translate>Error while confirming your email</translate></div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label><translate>Confirmation code</translate></label>
            <input type="text" required v-model="key" />
          </div>
          <router-link :to="{path: '/login'}">
            <translate>Back to login</translate>
          </router-link>
          <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
            <translate>Confirm your email</translate></button>
        </form>
        <div v-else class="ui positive message">
          <div class="header"><translate>Email confirmed</translate></div>
          <p><translate>Your email address was confirmed, you can now use the service without limitations.</translate></p>
          <router-link :to="{name: 'login'}">
            <translate>Proceed to login</translate>
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
