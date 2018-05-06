<template>
  <div class="main pusher" v-title="$t('Change your password')">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>{{ $t('Change your password') }}</h2>
        <form v-if="!success" class="ui form" @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header">{{ $('Error while changing your password') }}</div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <template v-if="token && uid">
            <div class="field">
              <label>{{ $t('New password') }}</label>
              <password-input v-model="newPassword" />
            </div>
            <router-link :to="{path: '/login'}">
              {{ $t('Back to login') }}
            </router-link>
            <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
              {{ $t('Update your password') }}</button>
          </template>
          <template v-else>
            <p>{{ $t('If the email address provided in the previous step is valid and binded to a user account, you should receive an email with reset instructions in the next couple of minutes.') }}</p>
          </template>
        </form>
        <div v-else class="ui positive message">
          <div class="header">{{ $t('Password updated successfully') }}</div>
          <p>{{ $t('Your password has been updated successfully.') }}</p>
          <router-link :to="{name: 'login'}">
            {{ $t('Proceed to login') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import PasswordInput from '@/components/forms/PasswordInput'

export default {
  props: ['defaultToken', 'defaultUid'],
  components: {
    PasswordInput
  },
  data () {
    return {
      newPassword: '',
      isLoading: false,
      errors: [],
      token: this.defaultToken,
      uid: this.defaultUid,
      success: false
    }
  },
  methods: {
    submit () {
      let self = this
      self.isLoading = true
      self.errors = []
      let payload = {
        uid: this.uid,
        token: this.token,
        new_password1: this.newPassword,
        new_password2: this.newPassword
      }
      return axios.post('auth/password/reset/confirm/', payload).then(response => {
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
