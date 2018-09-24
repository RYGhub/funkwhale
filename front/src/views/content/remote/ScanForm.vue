<template>
  <form class="ui form" @submit.prevent="scan">
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header"><translate>Error while fetching remote library</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="ui field">
      <label><translate>Search a remote library</translate></label>
      <div :class="['ui', 'action', {loading: isLoading}, 'input']">
        <input v-model="query" :placeholder="labels.placeholder" type="url">
        <button type="submit" class="ui icon button">
          <i class="search icon"></i>
        </button>
      </div>
    </div>
  </form>
</template>
<script>
import axios from 'axios'

export default {
  data () {
    return {
      query: '',
      isLoading: false,
      errors: []
    }
  },
  methods: {
    scan () {
      if (!this.query) {
        return
      }
      let self = this
      axios.post('federation/libraries/fetch/', {fid: this.query}).then((response) => {
        self.$emit('scanned', response.data)
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    labels () {
      let placeholder = this.$gettext('Enter a library url')
      return {
        placeholder
      }
    }
  }
}
</script>
