<template>
  <form
    :class="['ui', {'loading': isLoadingInstanceSetting}, 'form']"
    @submit.prevent="submit()">
    <p class="ui message" v-if="!$store.state.instance.settings.users.registration_enabled.value">
      <translate translate-context="Content/Signup/Form/Paragraph">Public registrations are not possible on this instance. You will need an invitation code to sign up.</translate>
    </p>

    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header"><translate translate-context="Content/Signup/Form/Paragraph">Your account cannot be created.</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="field">
      <label><translate translate-context="Content/*/*">Username</translate></label>
      <input
      ref="username"
      name="username"
      required
      type="text"
      autofocus
      :placeholder="labels.usernamePlaceholder"
      v-model="username">
    </div>
    <div class="field">
      <label><translate translate-context="Content/*/*/Noun">Email</translate></label>
      <input
      ref="email"
      name="email"
      required
      type="email"
      :placeholder="labels.emailPlaceholder"
      v-model="email">
    </div>
    <div class="field">
      <label><translate translate-context="Content/*/Input.Label">Password</translate></label>
      <password-input v-model="password" />
    </div>
    <div class="field" v-if="!$store.state.instance.settings.users.registration_enabled.value">
      <label><translate translate-context="Content/*/Input.Label">Invitation code</translate></label>
      <input
      required
      type="text"
      name="invitation"
      :placeholder="labels.placeholder"
      v-model="invitation">
    </div>
    <button :class="['ui', buttonClasses, {'loading': isLoading}, ' right floated button']" type="submit">
      <translate translate-context="Content/Signup/Button.Label">Create my account</translate>
    </button>
  </form>
</template>

<script>
import axios from "axios"
import logger from "@/logging"

import PasswordInput from "@/components/forms/PasswordInput"

export default {
  props: {
    defaultInvitation: { type: String, required: false, default: null },
    next: { type: String, default: "/" },
    buttonClasses: { type: String, default: "green" },
  },
  components: {
    PasswordInput
  },
  data() {
    return {
      username: "",
      email: "",
      password: "",
      isLoadingInstanceSetting: true,
      errors: [],
      isLoading: false,
      invitation: this.defaultInvitation
    }
  },
  created() {
    let self = this
    this.$store.dispatch("instance/fetchSettings", {
      callback: function() {
        self.isLoadingInstanceSetting = false
      }
    })
  },
  computed: {
    labels() {
      let placeholder = this.$pgettext(
        "Content/Signup/Form/Placeholder",
        "Enter your invitation code (case insensitive)"
      )
      let usernamePlaceholder = this.$pgettext("Content/Signup/Form/Placeholder", "Enter your username")
      let emailPlaceholder = this.$pgettext("Content/Signup/Form/Placeholder", "Enter your email")
      return {
        usernamePlaceholder,
        emailPlaceholder,
        placeholder
      }
    }
  },
  methods: {
    submit() {
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
      return axios.post("auth/registration/", payload).then(
        response => {
          logger.default.info("Successfully created account")
          self.$router.push({
            name: "profile",
            params: {
              username: this.username
            }
          })
        },
        error => {
          self.errors = error.backendErrors
          self.isLoading = false
        }
      )
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
