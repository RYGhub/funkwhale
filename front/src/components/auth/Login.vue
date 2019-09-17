<template>
  <main class="main pusher" v-title="labels.title">
    <section class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><translate translate-context="Content/Login/Title/Verb">Log in to your Funkwhale account</translate></h2>
        <form class="ui form" @submit.prevent="submit()">
          <div v-if="error" class="ui negative message">
            <div class="header"><translate translate-context="Content/Login/Error message.Title">We cannot log you in</translate></div>
            <ul class="list">
              <li v-if="error == 'invalid_credentials'"><translate translate-context="Content/Login/Error message.List item/Call to action">Please double-check your username/password couple is correct</translate></li>
              <li v-else>{{ error }}</li>
            </ul>
          </div>
          <div class="field">
            <label>
              <translate translate-context="Content/Login/Input.Label/Noun">Username or email</translate> |
              <router-link :to="{path: '/signup'}">
                <translate translate-context="*/Signup/Link/Verb">Create an account</translate>
              </router-link>
            </label>
            <input
            ref="username"
            tabindex="1"
            required
            name="username"
            type="text"
            autofocus
            :placeholder="labels.usernamePlaceholder"
            v-model="credentials.username"
            >
          </div>
          <div class="field">
            <label>
              <translate translate-context="Content/*/Input.Label">Password</translate> |
              <router-link :to="{name: 'auth.password-reset', query: {email: credentials.username}}">
                <translate translate-context="*/Login/*/Verb">Reset your password</translate>
              </router-link>
            </label>
            <password-input :index="2" required v-model="credentials.password" />

          </div>
          <button tabindex="3" :class="['ui', {'loading': isLoading}, 'right', 'floated', 'green', 'button']" type="submit">
             <translate translate-context="*/Login/*/Verb">Login</translate>
          </button>
        </form>
      </div>
    </section>
  </main>
</template>

<script>
import PasswordInput from "@/components/forms/PasswordInput"

export default {
  props: {
    next: { type: String, default: "/library" }
  },
  components: {
    PasswordInput
  },
  data() {
    return {
      // We need to initialize the component with any
      // properties that will be used in it
      credentials: {
        username: "",
        password: ""
      },
      error: "",
      isLoading: false
    }
  },
  created () {
    if (this.$store.state.auth.authenticated) {
      this.$router.push(this.next)
    }
  },
  mounted() {
    this.$refs.username.focus()
  },
  computed: {
    labels() {
      let usernamePlaceholder = this.$pgettext('Content/Login/Input.Placeholder', "Enter your username or email")
      let title = this.$pgettext('Head/Login/Title', "Log In")
      return {
        usernamePlaceholder,
        title
      }
    }
  },
  methods: {
    submit() {
      var self = this
      self.isLoading = true
      this.error = ""
      var credentials = {
        username: this.credentials.username,
        password: this.credentials.password
      }
      this.$store
        .dispatch("auth/login", {
          credentials,
          next: this.next,
          onError: error => {
            if (error.response.status === 400) {
              self.error = "invalid_credentials"
            } else {
              self.error = error.backendErrors[0]
            }
          }
        })
        .then(e => {
          self.isLoading = false
        })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
