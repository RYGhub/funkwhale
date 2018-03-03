<template>
  <div class="main pusher">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>Create a funkwhale account</h2>
        <form
          v-if="$store.state.instance.settings.users.registration_enabled.value"
          :class="['ui', {'loading': isLoadingInstanceSetting}, 'form']"
          @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">We cannot create your account</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label>Username</label>
            <input
            ref="username"
            required
            type="text"
            autofocus
            placeholder="Enter your username"
            v-model="username">
          </div>
          <div class="field">
            <label>Email</label>
            <input
            ref="email"
            required
            type="email"
            placeholder="Enter your email"
            v-model="email">
          </div>
          <div class="field">
            <label>Password</label>
            <div class="ui action input">
              <input
              required
              :type="passwordInputType"
              placeholder="Enter your password"
              v-model="password">
              <span @click="showPassword = !showPassword" title="Show/hide password" class="ui icon button">
                <i class="eye icon"></i>
              </span>
            </div>
          </div>
          <button :class="['ui', 'green', {'loading': isLoading}, 'button']" type="submit">Create my account</button>
        </form>
        <p v-else>Registration is currently disabled on this instance, please try again later.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'

export default {
  name: 'login',
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
      isLoading: false,
      showPassword: false
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
  },
  computed: {
    passwordInputType () {
      if (this.showPassword) {
        return 'text'
      }
      return 'password'
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
