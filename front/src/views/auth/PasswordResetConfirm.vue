<template>
  <main class="main pusher" v-title="labels.changePassword">
    <section class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><translate>Change your password</translate></h2>
        <form v-if="!success" class="ui form" @submit.prevent="submit()">
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header"><translate>Error while changing your password</translate></div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <template v-if="token && uid">
            <div class="field">
              <label><translate>New password</translate></label>
              <password-input v-model="newPassword" />
            </div>
            <router-link :to="{path: '/login'}">
              <translate>Back to login</translate>
            </router-link>
            <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
              <translate>Update your password</translate></button>
          </template>
          <template v-else>
            <p><translate>If the email address provided in the previous step is valid and binded to a user account, you should receive an email with reset instructions in the next couple of minutes.</translate></p>
          </template>
        </form>
        <div v-else class="ui positive message">
          <div class="header"><translate>Password updated successfully</translate></div>
          <p><translate>Your password has been updated successfully.</translate></p>
          <router-link :to="{name: 'login'}">
            <translate>Proceed to login</translate>
          </router-link>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from "axios"
import PasswordInput from "@/components/forms/PasswordInput"

export default {
  props: ["defaultToken", "defaultUid"],
  components: {
    PasswordInput
  },
  data() {
    return {
      newPassword: "",
      isLoading: false,
      errors: [],
      token: this.defaultToken,
      uid: this.defaultUid,
      success: false
    }
  },
  computed: {
    labels() {
      return {
        changePassword: this.$gettext("Change your password")
      }
    }
  },
  methods: {
    submit() {
      let self = this
      self.isLoading = true
      self.errors = []
      let payload = {
        uid: this.uid,
        token: this.token,
        new_password1: this.newPassword,
        new_password2: this.newPassword
      }
      return axios.post("auth/password/reset/confirm/", payload).then(
        response => {
          self.isLoading = false
          self.success = true
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
