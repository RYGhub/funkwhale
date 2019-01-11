<template>
  <form class="ui form" @submit.prevent="submit">
    <p v-if="!library"><translate>Libraries help you organize and share your music collections. You can upload your own music collection to Funkwhale and share it with your friends and family.</translate></p>
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header"><translate>Error</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="required field">
      <label><translate>Name</translate></label>
      <input v-model="currentName" :placeholder="labels.namePlaceholder" required maxlength="100">
    </div>
    <div class="field">
      <label><translate>Description</translate></label>
      <textarea v-model="currentDescription" :placeholder="labels.descriptionPlaceholder" maxlength="2000"></textarea>
    </div>
    <div class="field">
      <label><translate>Visibility</translate></label>
      <p><translate>You are able to share your library with other people, regardless of its visibility.</translate></p>
      <select class="ui dropdown" v-model="currentVisibilityLevel">
        <option :value="c" v-for="c in ['me', 'instance', 'everyone']">{{ labels.visibility[c] }}</option>
      </select>
    </div>
    <button class="ui submit button" type="submit">
      <translate v-if="library">Update library</translate>
      <translate v-else>Create library</translate>
    </button>
    <dangerous-button v-if="library" class="right floated basic button" color='red' @confirm="remove()">
      <translate>Delete</translate>
      <p slot="modal-header">
        <translate>Delete this library?</translate>
      </p>
      <p slot="modal-content">
        <translate>
          The library and all its tracks will be deleted. This can not be undone.
        </translate>
      </p>
      <p slot="modal-confirm">
        <translate>Delete library</translate>
      </p>
    </dangerous-button>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  props: ['library'],
  data () {
    let d = {
      isLoading: false,
      over: false,
      errors: []
    }
    if (this.library) {
      d.currentVisibilityLevel = this.library.privacy_level
      d.currentName = this.library.name
      d.currentDescription = this.library.description
    } else {
      d.currentVisibilityLevel = 'me'
      d.currentName = ''
      d.currentDescription = ''
    }
    return d
  },
  computed: {
    labels () {
      let namePlaceholder = this.$gettext('My awesome library')
      let descriptionPlaceholder = this.$gettext('This library contains my personal music, I hope you like it.')
      let me = this.$gettext('Nobody except me')
      let instance = this.$gettext('Everyone on this instance')
      let everyone = this.$gettext('Everyone, across all instances')
      return {
        namePlaceholder,
        descriptionPlaceholder,
        visibility: {
          me,
          instance,
          everyone
        }
      }
    }
  },
  methods: {
    submit () {
      let self = this
      this.isLoading = true
      let payload = {
        name: this.currentName,
        description: this.currentDescription,
        privacy_level: this.currentVisibilityLevel
      }
      let promise
      if (this.library) {
        promise = axios.patch(`libraries/${this.library.uuid}/`, payload)
      } else {
        promise = axios.post('libraries/', payload)
      }
      promise.then((response) => {
        self.isLoading = false
        let msg
        if (self.library) {
          self.$emit('updated', response.data)
          msg = this.$gettext('Library updated')
        } else {
          self.$emit('created', response.data)
          msg = this.$gettext('Library created')
        }
        self.$store.commit('ui/addMessage', {
          content: msg,
          date: new Date()
        })
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    reset () {
      this.currentVisibilityLevel = 'me'
      this.currentName = ''
      this.currentDescription = ''
    },
    remove () {
      let self = this
      axios.delete(`libraries/${this.library.uuid}/`).then((response) => {
        self.isLoading = false
        let msg = this.$gettext('Library deleted')
        self.$emit('deleted', {})
        self.$store.commit('ui/addMessage', {
          content: msg,
          date: new Date()
        })
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  }
}
</script>

<style scoped>
</style>
