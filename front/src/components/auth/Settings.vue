<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2 class="ui header">
          <translate>Account settings</translate>
        </h2>
        <form class="ui form" @submit.prevent="submitSettings()">
          <div v-if="settings.success" class="ui positive message">
            <div class="header">
              <translate>Settings updated</translate>
            </div>
          </div>
          <div v-if="settings.errors.length > 0" class="ui negative message">
            <div class="header"><translate>We cannot save your settings</translate></div>
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
          <button :class="['ui', {'loading': isLoading}, 'button']" type="submit">
            <translate>Update settings</translate>
          </button>
        </form>
      </div>
      <div class="ui hidden divider"></div>
      <div class="ui small text container">
        <h2 class="ui header">
          <translate>Avatar</translate>
        </h2>
        <div class="ui form">
          <div v-if="avatarErrors.length > 0" class="ui negative message">
            <div class="header"><translate>We cannot save your avatar</translate></div>
            <ul class="list">
              <li v-for="error in avatarErrors">{{ error }}</li>
            </ul>
          </div>
          <div class="ui stackable grid">
            <div class="ui ten wide column">
              <h3 class="ui header"><translate>Upload a new avatar</translate></h3>
              <p><translate>PNG, GIF or JPG. At most 2MB. Will be downscaled to 400x400px.</translate></p>
              <input class="ui input" ref="avatar" type="file" />
              <div class="ui hidden divider"></div>
              <button @click="submitAvatar" :class="['ui', {'loading': isLoadingAvatar}, 'button']">
                <translate>Update avatar</translate>
              </button>
            </div>
            <div class="ui six wide column">
              <h3 class="ui header"><translate>Current avatar</translate></h3>
              <img class="ui circular image" v-if="currentAvatar && currentAvatar.square_crop" :src="$store.getters['instance/absoluteUrl'](currentAvatar.medium_square_crop)" />
              <div class="ui hidden divider"></div>
              <button @click="removeAvatar" v-if="currentAvatar && currentAvatar.square_crop" :class="['ui', {'loading': isLoadingAvatar}, ,'yellow', 'button']">
                <translate>Remove avatar</translate>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="ui hidden divider"></div>
      <div class="ui small text container">
        <h2 class="ui header">
          <translate>Change my password</translate>
        </h2>
        <div class="ui message">
          <translate>Changing your password will also change your Subsonic API password if you have requested one.</translate>
          <translate>You will have to update your password on your clients that use this password.</translate>
        </div>
        <form class="ui form" @submit.prevent="submitPassword()">
          <div v-if="passwordError" class="ui negative message">
            <div class="header">
              <translate>Cannot change your password</translate>
            </div>
            <ul class="list">
              <li v-if="passwordError == 'invalid_credentials'"><translate>Please double-check your password is correct</translate></li>
            </ul>
          </div>
          <div class="field">
            <label><translate>Old password</translate></label>
            <password-input required v-model="old_password" />

          </div>
          <div class="field">
            <label><translate>New password</translate></label>
            <password-input required v-model="new_password" />
          </div>
          <dangerous-button
            color="yellow"
            :class="['ui', {'loading': isLoading}, 'button']"
            :action="submitPassword">
            <translate>Change password</translate>
            <p slot="modal-header"><translate>Change your password?</translate></p>
            <div slot="modal-content">
              <p><translate>Changing your password will have the following consequences</translate></p>
              <ul>
                <li><translate>You will be logged out from this session and have to log in with the new one</translate></li>
                <li><translate>Your Subsonic password will be changed to a new, random one, logging you out from devices that used the old Subsonic password</translate></li>
              </ul>
            </div>
            <p slot="modal-confirm"><translate>Disable access</translate></p>
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
      currentAvatar: this.$store.state.auth.profile.avatar,
      passwordError: '',
      isLoading: false,
      isLoadingAvatar: false,
      avatarErrors: [],
      avatar: null,
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
    submitAvatar () {
      this.isLoadingAvatar = true
      this.avatarErrors = []
      let self = this
      this.avatar = this.$refs.avatar.files[0]
      let formData = new FormData()
      formData.append('avatar', this.avatar)
      axios.patch(
        `users/users/${this.$store.state.auth.username}/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      ).then(response => {
        this.isLoadingAvatar = false
        self.currentAvatar = response.data.avatar
        self.$store.commit('auth/avatar', self.currentAvatar)
      }, error => {
        self.isLoadingAvatar = false
        self.avatarErrors = error.backendErrors
      })
    },
    removeAvatar () {
      this.isLoadingAvatar = true
      let self = this
      this.avatar = null
      axios.patch(
        `users/users/${this.$store.state.auth.username}/`,
        {avatar: null}
      ).then(response => {
        this.isLoadingAvatar = false
        self.currentAvatar = {}
        self.$store.commit('auth/avatar', self.currentAvatar)
      }, error => {
        self.isLoadingAvatar = false
        self.avatarErrors = error.backendErrors
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
    labels () {
      return {
        title: this.$gettext('Account Settings')
      }
    },
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
