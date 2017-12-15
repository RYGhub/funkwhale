<template>
  <div class="main pusher">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>Log in to your Funkwhale account</h2>
        <form class="ui form" @submit.prevent="submit()">
          <div v-if="error" class="ui negative message">
            <div class="header">We cannot log you in</div>
            <ul class="list">
              <li v-if="error == 'invalid_credentials'">Please double-check your username/password couple is correct</li>
              <li v-else>An unknown error happend, this can mean the server is down or cannot be reached</li>
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
            v-model="credentials.username"
            >
          </div>
          <div class="field">
            <label>Password</label>
            <input
            required
            type="password"
            placeholder="Enter your password"
            v-model="credentials.password"
            >
          </div>
          <button :class="['ui', {'loading': isLoading}, 'button']" type="submit">Login</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import auth from '@/auth'

export default {
  name: 'login',
  props: {
    next: {type: String}
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
      auth.login(this, credentials, {path: this.next}, function (response) {
        // error callback
        if (response.status === 400) {
          self.error = 'invalid_credentials'
        } else {
          self.error = 'unknown_error'
        }
      }).then((response) => {
        self.isLoading = false
      })
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
