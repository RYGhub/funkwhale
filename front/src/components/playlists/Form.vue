<template>
  <form class="ui form" @submit.prevent="submit()">
    <h4 v-if="title" class="ui header">{{ $gettext('Create a new playlist') }}</h4>
    <div v-if="success" class="ui positive message">
      <div class="header">
        <template v-if="playlist">
          {{ $gettext('Playlist updated') }}
        </template>
        <template v-else>
          {{ $gettext('Playlist created') }}
        </template>
      </div>
    </div>
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header">{{ $gettext('We cannot create the playlist') }}</div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="three fields">
      <div class="field">
        <label>{{ $gettext('Playlist name') }}</label>
        <input v-model="name" required type="text" placeholder="My awesome playlist" />
      </div>
      <div class="field">
        <label>{{ $gettext('Playlist visibility') }}</label>
        <select class="ui dropdown" v-model="privacyLevel">
          <option :value="c.value" v-for="c in privacyLevelChoices">{{ c.label }}</option>
        </select>
      </div>
      <div class="field">
        <label>&nbsp;</label>
        <button :class="['ui', 'fluid', {'loading': isLoading}, 'button']" type="submit">
          <template v-if="playlist">{{ $gettext('Update playlist') }}</template>
          <template v-else>{{ $gettext('Create playlist') }}</template>
        </button>
      </div>
    </div>
  </form>
</template>

<script>
import $ from 'jquery'
import axios from 'axios'

import logger from '@/logging'

export default {
  props: {
    title: {type: Boolean, default: true},
    playlist: {type: Object, default: null}
  },
  mounted () {
    $(this.$el).find('.dropdown').dropdown()
  },
  data () {
    let d = {
      errors: [],
      success: false,
      isLoading: false
    }
    if (this.playlist) {
      d.name = this.playlist.name
      d.privacyLevel = this.playlist.privacy_level
    } else {
      d.privacyLevel = this.$store.state.auth.profile.privacy_level
      d.name = ''
    }
    return d
  },
  computed: {
    privacyLevelChoices: function () {
      return [
        {
          value: 'me',
          label: this.$gettext('Nobody except me')
        },
        {
          value: 'instance',
          label: this.$gettext('Everyone on this instance')
        },
        {
          value: 'everyone',
          label: this.$gettext('Everyone')
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

      let promise
      let url
      if (this.playlist) {
        url = `playlists/${this.playlist.id}/`
        promise = axios.patch(url, payload)
      } else {
        url = 'playlists/'
        promise = axios.post(url, payload)
      }
      return promise.then(response => {
        self.success = true
        self.isLoading = false
        if (!self.playlist) {
          self.name = ''
        }
        self.$emit('updated', response.data)
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
