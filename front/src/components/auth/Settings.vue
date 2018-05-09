<template>
  <div class="main pusher" v-title="'Account Settings'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2 class="ui header"><i18next path="Account settings"/></h2>
        <form class="ui form" @submit.prevent="submitSettings()">
          <div v-if="settings.success" class="ui positive message">
            <div class="header"><i18next path="Settings updated"/></div>
          </div>
          <div v-if="settings.errors.length > 0" class="ui negative message">
            <i18next tag="div" class="header" path="We cannot save your settings"/>
            <ul class="list">
              <li v-for="error in settings.errors">{{ error }}</li>
            </ul>
          </div>
          <div class="field" v-for="f in orderedSettingsFields">
            <label :for="f.id">{{ f.label }}</label>
            <p v-if="f.help">{{ f.help }}</p>
            <select v-if="f.type === 'dropdown'" class="ui dropdown" v-model="f.value">
              <option :value="c.value" v-for="c in f.choices">{{ c.label }}</option>
            </select>
          </div>
          <button :class="['ui', {'loading': isLoading}, 'button']" type="submit"><i18next path="Update settings"/></button>
        </form>
      </div>
      <div class="ui hidden divider"></div>
      <div class="ui small text container">
        <h2 class="ui header"><i18next path="Change my password"/></h2>
        <div class="ui message">
          {{ $t('Changing your password will also change your Subsonic API password if you have requested one.') }}
          {{ $t('You will have to update your password on your clients that use this password.') }}
        </div>
        <form class="ui form" @submit.prevent="submitPassword()">
          <div v-if="passwordError" class="ui negative message">
            <div class="header"><i18next path="Cannot change your password"/></div>
            <ul class="list">
              <i18next tag="li" v-if="passwordError == 'invalid_credentials'" path="Please double-check your password is correct"/>
            </ul>
          </div>
          <div class="field">
            <label><i18next path="Old password"/></label>
            <password-input required v-model="old_password" />

          </div>
          <div class="field">
            <label><i18next path="New password"/></label>
            <password-input required v-model="new_password" />
          </div>
          <dangerous-button
            color="yellow"
            :class="['ui', {'loading': isLoading}, 'button']"
            :action="submitPassword">
            {{ $t('Change password') }}
            <p slot="modal-header">{{ $t('Change your password?') }}</p>
            <div slot="modal-content">
              <p>{{ $t("Changing your password will have the following consequences") }}</p>
              <ul>
                <li>{{ $t('You will be logged out from this session and have to log out with the new one') }}</li>
                <li>{{ $t('Your Subsonic password will be changed to a new, random one, logging you out from devices that used the old Subsonic password') }}</li>
              </ul>
            </div>
            <p slot="modal-confirm">{{ $t('Disable access') }}</p>
          </dangerous-button>
        </form>
        <div class="ui hidden divider" />
        <subsonic-token-form />
      </div>
    </div>
  </div>
</template>

<script>
import $ from 'jquery'
import axios from 'axios'
import logger from '@/logging'
import PasswordInput from '@/components/forms/PasswordInput'
import SubsonicTokenForm from '@/components/auth/SubsonicTokenForm'

export default {
  components: {
    PasswordInput,
    SubsonicTokenForm
  },
  data () {
    let d = {
      // We need to initialize the component with any
      // properties that will be used in it
      old_password: '',
      new_password: '',
      passwordError: '',
      isLoading: false,
      settings: {
        success: false,
        errors: [],
        order: ['privacy_level'],
        fields: {
          'privacy_level': {
            type: 'dropdown',
            initial: this.$store.state.auth.profile.privacy_level,
            label: 'Activity visibility',
            help: 'Determine the visibility level of your activity',
            choices: [
              {
                value: 'me',
                label: 'Nobody except me'
              },
              {
                value: 'instance',
                label: 'Everyone on this instance'
              }
            ]
          }
        }
      }
    }
    d.settings.order.forEach(id => {
      d.settings.fields[id].value = d.settings.fields[id].initial
    })
    return d
  },
  mounted () {
    $('select.dropdown').dropdown()
  },
  methods: {
    submitSettings () {
      this.settings.success = false
      this.settings.errors = []
      let self = this
      let payload = this.settingsValues
      let url = `users/users/${this.$store.state.auth.username}/`
      return axios.patch(url, payload).then(response => {
        logger.default.info('Updated settings successfully')
        self.settings.success = true
      }, error => {
        logger.default.error('Error while updating settings')
        self.isLoading = false
        self.settings.errors = error.backendErrors
      })
    },
    submitPassword () {
      var self = this
      self.isLoading = true
      this.error = ''
      var credentials = {
        old_password: this.old_password,
        new_password1: this.new_password,
        new_password2: this.new_password
      }
      let url = 'auth/registration/change-password/'
      return axios.post(url, credentials).then(response => {
        logger.default.info('Password successfully changed')
        self.$router.push({
          name: 'profile',
          params: {
            username: self.$store.state.auth.username
          }})
      }, error => {
        if (error.response.status === 400) {
          self.passwordError = 'invalid_credentials'
        } else {
          self.passwordError = 'unknown_error'
        }
        self.isLoading = false
      })
    }
  },
  computed: {
    orderedSettingsFields () {
      let self = this
      return this.settings.order.map(id => {
        return self.settings.fields[id]
      })
    },
    settingsValues () {
      let self = this
      let s = {}
      this.settings.order.forEach(setting => {
        let conf = self.settings.fields[setting]
        s[setting] = conf.value
      })
      return s
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
