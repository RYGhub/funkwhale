<template>
  <form class="ui form" @submit.prevent="submit()">
    <h4 class="ui header">Create a new playlist</h4>
    <div v-if="success" class="ui positive message">
      <div class="header">Playlist created</div>
    </div>
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header">We cannot create the playlist</div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="fields">
      <div class="field">
        <label>Playlist name</label>
        <input v-model="name" required type="text" placeholder="My awesome playlist" />
      </div>
      <div class="field">
        <label>Playlist visibility</label>
        <select class="ui dropdown" v-model="privacyLevel">
          <option :value="c.value" v-for="c in privacyLevelChoices">{{ c.label }}</option>
        </select>
      </div>
    </div>
    <button :class="['ui', {'loading': isLoading}, 'button']" type="submit">Create playlist</button>
  </form>
</template>

<script>
import $ from 'jquery'
import axios from 'axios'

import logger from '@/logging'

export default {
  mounted () {
    $(this.$el).find('.dropdown').dropdown()
  },
  data () {
    return {
      privacyLevel: this.$store.state.auth.profile.privacy_level,
      name: '',
      errors: [],
      success: false,
      isLoading: false,
      privacyLevelChoices: [
        {
          value: 'me',
          label: 'Nobody except me'
        },
        {
          value: 'instance',
          label: 'Everyone on this instance'
        },
        {
          value: 'everyone',
          label: 'Everyone'
        }
      ]
    }
  },
  methods: {
    submit () {
      this.isLoading = true
      this.success = false
      this.errors = []
      let self = this
      let payload = {
        name: this.name,
        privacy_level: this.privacyLevel
      }
      let url = `playlists/`
      return axios.post(url, payload).then(response => {
        logger.default.info('Successfully created playlist')
        self.success = true
        self.isLoading = false
        self.$store.dispatch('playlists/fetchOwn')
      }, error => {
        logger.default.error('Error while creating playlist')
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
