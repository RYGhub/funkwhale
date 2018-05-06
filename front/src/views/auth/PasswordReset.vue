<template>
  <div class="main pusher" v-title="$t('Reset your password')">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>{{ $t('Reset your password') }}</h2>
        <form class="ui form" @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">{{ $('Error while asking for a password reset') }}</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <p>{{ $t('Use this form to request a password reset. We will send an email to the given address with instructions to reset your password.') }}</p>
          <div class="field">
            <label>{{ $t('Account\'s email') }}</label>
            <input
              required
              ref="email"
              type="email"
              autofocus
              :placeholder="$t('Input the email address binded to your account')"
              v-model="email">
          </div>
          <router-link :to="{path: '/login'}">
            {{ $t('Back to login') }}
          </router-link>
          <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
            {{ $t('Ask for a password reset') }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['defaultEmail'],
  data () {
    return {
      email: this.defaultEmail,
      isLoading: false,
      errors: []
    }
  },
  mounted () {
    this.$refs.email.focus()
  },
  methods: {
    submit () {
      let self = this
      self.isLoading = true
      self.errors = []
      let payload = {
        email: this.email
      }
      return axios.post('auth/password/reset/', payload).then(response => {
        self.isLoading = false
        self.$router.push({
          name: 'auth.password-reset-confirm'
        })
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
