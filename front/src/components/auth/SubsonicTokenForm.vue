<template>
  <form class="ui form" @submit.prevent="requestNewToken()">
    <h2><translate :translate-context="'Content/Settings/Title'">Subsonic API password</translate></h2>
    <p class="ui message" v-if="!subsonicEnabled">
      <translate :translate-context="'Content/Settings/Paragraph'">The Subsonic API is not available on this Funkwhale instance.</translate>
    </p>
    <p>
      <translate :translate-context="'Content/Settings/Paragraph'">Funkwhale is compatible with other music players that support the Subsonic API.</translate>&nbsp;<translate :translate-context="'Content/Settings/Paragraph'">You can use those to enjoy your playlist and music in offline mode, on your smartphone or tablet, for instance.</translate>
    </p>
    <p>
      <translate :translate-context="'Content/Settings/Paragraph'">However, accessing Funkwhale from those clients require a separate password you can set below.</translate>
    </p>
    <p><a href="https://docs.funkwhale.audio/users/apps.html#subsonic-compatible-clients" target="_blank">
      <translate :translate-context="'Content/Settings/Link'">Discover how to use Funkwhale from other apps</translate>
    </a></p>
    <div v-if="success" class="ui positive message">
      <div class="header">{{ successMessage }}</div>
    </div>
    <div v-if="subsonicEnabled && errors.length > 0" class="ui negative message">
      <div class="header"><translate :translate-context="'Content/Settings/Error message.Title'">Error</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <template v-if="subsonicEnabled">
      <div v-if="token" class="field">
        <password-input v-model="token" />
      </div>
      <dangerous-button
        v-if="token"
        color="grey"
        :class="['ui', {'loading': isLoading}, 'button']"
        :action="requestNewToken">
        <translate :translate-context="'Content/Settings/Button.Label/Verb'">Request a new password</translate>
        <p slot="modal-header"><translate :translate-context="'Popup/Settings/Title'">Request a new Subsonic API password?</translate></p>
        <p slot="modal-content"><translate :translate-context="'Popup/Settings/Paragraph'">This will log you out from existing devices that use the current password.</translate></p>
        <p slot="modal-confirm"><translate :translate-context="'Popup/Settings/Button.Label/Verb'">Request a new password</translate></p>
      </dangerous-button>
      <button
        v-else
        color="grey"
        :class="['ui', {'loading': isLoading}, 'button']"
        @click="requestNewToken"><translate :translate-context="'Content/Settings/Button.Label/Verb'">Request a password</translate></button>
        <dangerous-button
          v-if="token"
          color="yellow"
          :class="['ui', {'loading': isLoading}, 'button']"
          :action="disable">
          <translate :translate-context="'Content/Settings/Button.Label/Verb'">Disable Subsonic access</translate>
          <p slot="modal-header"><translate :translate-context="'Popup/Settings/Title'">Disable Subsonic API access?</translate></p>
          <p slot="modal-content"><translate :translate-context="'Popup/Settings/Paragraph'">This will completely disable access to the Subsonic API using from account.</translate></p>
          <p slot="modal-confirm"><translate :translate-context="'Popup/Settings/Button.Label'">Disable access</translate></p>
        </dangerous-button>
    </template>
  </form>
</template>

<script>
import axios from 'axios'
import PasswordInput from '@/components/forms/PasswordInput'

export default {
  components: {
    PasswordInput
  },
  data () {
    return {
      token: null,
      errors: [],
      success: false,
      isLoading: false,
      successMessage: ''
    }
  },
  created () {
    this.fetchToken()
  },
  methods: {
    fetchToken () {
      this.success = false
      this.errors = []
      this.isLoading = true
      let self = this
      let url = `users/users/${this.$store.state.auth.username}/subsonic-token/`
      return axios.get(url).then(response => {
        self.token = response.data['subsonic_api_token']
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    requestNewToken () {
      this.successMessage = this.$pgettext('Content/Settings/Message', 'Password updated')
      this.success = false
      this.errors = []
      this.isLoading = true
      let self = this
      let url = `users/users/${this.$store.state.auth.username}/subsonic-token/`
      return axios.post(url, {}).then(response => {
        self.token = response.data['subsonic_api_token']
        self.isLoading = false
        self.success = true
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    disable () {
      this.successMessage = this.$pgettext('Content/Settings/Message', 'Access disabled')
      this.success = false
      this.errors = []
      this.isLoading = true
      let self = this
      let url = `users/users/${this.$store.state.auth.username}/subsonic-token/`
      return axios.delete(url).then(response => {
        self.isLoading = false
        self.token = null
        self.success = true
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    subsonicEnabled () {
      return this.$store.state.instance.settings.subsonic.enabled.value
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
