<template>
  <div class="main pusher" v-title="'Sign Up'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><i18next path="Create a funkwhale account"/></h2>
        <form
          v-if="$store.state.instance.settings.users.registration_enabled.value"
          :class="['ui', {'loading': isLoadingInstanceSetting}, 'form']"
          @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header"><i18next path="We cannot create your account"/></div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <i18next tag="label" path="Username"/>
            <input
            ref="username"
            required
            type="text"
            autofocus
            placeholder="Enter your username"
            v-model="username">
          </div>
          <div class="field">
            <i18next tag="label" path="Email"/>
            <input
            ref="email"
            required
            type="email"
            placeholder="Enter your email"
            v-model="email">
          </div>
          <div class="field">
            <i18next tag="label" path="Password"/>
            <password-input v-model="password" />
          </div>
          <button :class="['ui', 'green', {'loading': isLoading}, 'button']" type="submit"><i18next path="Create my account"/></button>
        </form>
        <i18next v-else tag="p" path="Registration is currently disabled on this instance, please try again later."/>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'

import PasswordInput from '@/components/forms/PasswordInput'

export default {
  name: 'login',
  components: {
    PasswordInput
  },
  props: {
    next: {type: String, default: '/'}
  },
  data () {
    return {
      username: '',
      email: '',
      password: '',
      isLoadingInstanceSetting: true,
      errors: [],
      isLoading: false
    }
  },
  created () {
    let self = this
    this.$store.dispatch('instance/fetchSettings', {
      callback: function () {
        self.isLoadingInstanceSetting = false
      }
    })
  },
  methods: {
    submit () {
      var self = this
      self.isLoading = true
      this.errors = []
      var payload = {
        username: this.username,
        password1: this.password,
        password2: this.password,
        email: this.email
      }
      return axios.post('auth/registration/', payload).then(response => {
        logger.default.info('Successfully created account')
        self.$router.push({
          name: 'profile',
          params: {
            username: this.username
          }})
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
