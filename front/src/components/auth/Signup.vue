<template>
  <div class="main pusher" v-title="'Sign Up'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>{{ $t("Create a funkwhale account") }}</h2>
        <form
          :class="['ui', {'loading': isLoadingInstanceSetting}, 'form']"
          @submit.prevent="submit()">
          <p class="ui message" v-if="!$store.state.instance.settings.users.registration_enabled.value">
            {{ $t('Registration are closed on this instance, you will need an invitation code to signup.') }}
          </p>

          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">{{ $t("We cannot create your account") }}</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label>{{ $t("Username") }}</label>
            <input
            ref="username"
            required
            type="text"
            autofocus
            placeholder="Enter your username"
            v-model="username">
          </div>
          <div class="field">
            <label>{{ $t("Email") }}</label>
            <input
            ref="email"
            required
            type="email"
            placeholder="Enter your email"
            v-model="email">
          </div>
          <div class="field">
            <label>{{ $t("Password") }}</label>
            <password-input v-model="password" />
          </div>
          <div class="field">
            <label v-if="!$store.state.instance.settings.users.registration_enabled.value">{{ $t("Invitation code") }}</label>
            <label v-else>{{ $t("Invitation code (optional)") }}</label>
            <input
            :required="!$store.state.instance.settings.users.registration_enabled.value"
            type="text"
            :placeholder="$t('Enter your invitation code (case insensitive)')"
            v-model="invitation">
          </div>
          <button :class="['ui', 'green', {'loading': isLoading}, 'button']" type="submit">
            {{ $t("Create my account") }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'

import PasswordInput from '@/components/forms/PasswordInput'

export default {
  props: {
    invitation: {type: String, required: false, default: null},
    next: {type: String, default: '/'}
  },
  components: {
    PasswordInput
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
        email: this.email,
        invitation: this.invitation
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
