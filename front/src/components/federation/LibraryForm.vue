<template>
  <form class="ui form" @submit.prevent="fetchInstanceInfo">
    <h3 class="ui header">
      <translate>Federate with a new instance</translate>
    </h3>
    <p>
      <translate>Use this form to scan an instance and setup federation.</translate>
    </p>
    <div v-if="errors.length > 0 || scanErrors.length > 0" class="ui negative message">
      <div class="header">
        <translate>Error while scanning library</translate>
      </div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
        <li v-for="error in scanErrors">{{ error }}</li>
      </ul>
    </div>
    <div class="ui two fields">
      <div class="ui field">
        <label>
          <translate>Library name</translate>
        </label>
        <input v-model="libraryUsername" type="text" placeholder="library@demo.funkwhale.audio" />
      </div>
      <div class="ui field">
        <label>&nbsp;</label>
        <button
          type="submit"
          :disabled="isLoading"
          :class="['ui', 'icon', {loading: isLoading}, 'button']">
          <i class="search icon"></i>
          <translate>Launch scan</translate>
        </button>
      </div>
    </div>
  </form>
</template>

<script>
import axios from 'axios'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'
import Pagination from '@/components/Pagination'

export default {
  components: {
    TrackTable,
    RadioButton,
    Pagination
  },
  data () {
    return {
      isLoading: false,
      libraryUsername: '',
      result: null,
      errors: []
    }
  },
  methods: {
    follow () {
      let params = {
        'actor': this.result['actor']['id'],
        'autoimport': false,
        'download_files': false,
        'federation_enabled': true
      }
      let self = this
      self.isFollowing = false
      axios.post('/federation/libraries/', params).then((response) => {
        self.$emit('follow', {data: self.result, library: response.data})
        self.result = response.data
        self.isFollowing = false
      }, error => {
        self.isFollowing = false
        self.errors = error.backendErrors
      })
    },
    fetchInstanceInfo () {
      let self = this
      this.isLoading = true
      self.errors = []
      self.result = null
      axios.get('/federation/libraries/fetch/', {params: {account: this.libraryUsername.trim()}}).then((response) => {
        self.result = response.data
        self.result.display_name = self.libraryUsername
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  computed: {
    scanErrors () {
      let errors = []
      if (!this.result) {
        return errors
      }
      let keys = ['webfinger', 'actor', 'library']
      keys.forEach(k => {
        if (this.result[k]) {
          if (this.result[k].errors) {
            this.result[k].errors.forEach(e => {
              errors.push(e)
            })
          }
        }
      })
      return errors
    }
  },
  watch: {
    result (newValue, oldValue) {
      this.$emit('scanned', newValue)
    }
  }
}
</script>
