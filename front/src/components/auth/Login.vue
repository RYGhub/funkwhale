<template>
  <div class="main pusher" v-title="'Log In'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><i18next path="Log in to your Funkwhale account"/></h2>
        <form class="ui form" @submit.prevent="submit()">
          <div v-if="error" class="ui negative message">
            <div class="header"><i18next path="We cannot log you in"/></div>
            <ul class="list">
              <i18next tag="li" v-if="error == 'invalid_credentials'" path="Please double-check your username/password couple is correct"/>
              <i18next tag="li" v-else path="An unknown error happend, this can mean the server is down or cannot be reached"/>
            </ul>
          </div>
          <div class="field">
            <label>
              {{ $t('Username or email') }} |
              <router-link :to="{path: '/signup'}">
                {{ $t('Create an account') }}
              </router-link>
            </label>
            <input
            ref="username"
            tabindex="1"
            required
            type="text"
            autofocus
            placeholder="Enter your username or email"
            v-model="credentials.username"
            >
          </div>
          <div class="field">
            <label>
              {{ $t('Password') }} |
              <router-link :to="{name: 'auth.password-reset', query: {email: credentials.username}}">
                {{ $t('Reset your password') }}
              </router-link>
            </label>
            <password-input :index="2" required v-model="credentials.password" />

          </div>
          <button tabindex="3" :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit"><i18next path="Login"/></button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import PasswordInput from '@/components/forms/PasswordInput'

export default {
  props: {
    next: {type: String, default: '/'}
  },
  components: {
    PasswordInput
  },
  data () {
    return {
      // We need to initialize the component with any
      // properties that will be used in it
      credentials: {
        username: '',
        password: ''
      },
      error: '',
      isLoading: false
    }
  },
  mounted () {
    this.$refs.username.focus()
  },
  methods: {
    submit () {
      var self = this
      self.isLoading = true
      this.error = ''
      var credentials = {
        username: this.credentials.username,
        password: this.credentials.password
      }
      // We need to pass the component's this context
      // to properly make use of http in the auth service
      this.$store.dispatch('auth/login', {
        credentials,
        next: '/library',
        onError: error => {
          if (error.response.status === 400) {
            self.error = 'invalid_credentials'
          } else {
            self.error = 'unknown_error'
          }
        }
      }).then(e => {
        self.isLoading = false
      })
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
