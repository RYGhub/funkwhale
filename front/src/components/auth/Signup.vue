<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><translate>Create a funkwhale account</translate></h2>
        <form
          :class="['ui', {'loading': isLoadingInstanceSetting}, 'form']"
          @submit.prevent="submit()">
          <p class="ui message" v-if="!$store.state.instance.settings.users.registration_enabled.value">
            <translate>Registration are closed on this instance, you will need an invitation code to signup.</translate>
          </p>

          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header"><translate>We cannot create your account</translate></div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label><translate>Username</translate></label>
            <input
            ref="username"
            required
            type="text"
            autofocus
            :placeholder="labels.usernamePlaceholder"
            v-model="username">
          </div>
          <div class="field">
            <label><translate>Email</translate></label>
            <input
            ref="email"
            required
            type="email"
            :placeholder="labels.emailPlaceholder"
            v-model="email">
          </div>
          <div class="field">
            <label><translate>Password</translate></label>
            <password-input v-model="password" />
          </div>
          <div class="field">
            <label v-if="!$store.state.instance.settings.users.registration_enabled.value"><translate>Invitation code</translate></label>
            <label v-else><translate>Invitation code (optional)</translate></label>
            <input
            :required="!$store.state.instance.settings.users.registration_enabled.value"
            type="text"
            :placeholder="labels.placeholder"
            v-model="invitation">
          </div>
          <button :class="['ui', 'green', {'loading': isLoading}, 'button']" type="submit">
            <translate>Create my account</translate>
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
    defaultInvitation: {type: String, required: false, default: null},
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
      isLoading: false,
      invitation: this.defaultInvitation
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
  computed: {
    labels () {
      let title = this.$gettext('Sign Up')
      let placeholder = this.$gettext('Enter your invitation code (case insensitive)')
      let usernamePlaceholder = this.$gettext('Enter your username')
      let emailPlaceholder = this.$gettext('Enter your email')
      return {
        title,
        usernamePlaceholder,
        emailPlaceholder,
        placeholder
      }
    }
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
