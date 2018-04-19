<template>
  <div>
    <form v-if="!over" class="ui form" @submit.prevent="submit">
      <p>{{ $t('Something\'s missing in the library? Let us know what you would like to listen!') }}</p>
      <div class="required field">
        <label>{{ $t('Artist name') }}</label>
        <input v-model="currentArtistName" placeholder="The Beatles, Mickael Jackson…" required maxlength="200">
      </div>
      <div class="field">
        <label>{{ $t('Albums') }}</label>
        <p>{{ $t('Leave this field empty if you\'re requesting the whole discography.') }}</p>
        <input v-model="currentAlbums" placeholder="The White Album, Thriller…" maxlength="2000">
      </div>
      <div class="field">
        <label>{{ $t('Comment') }}</label>
        <textarea v-model="currentComment" rows="3" placeholder="Use this comment box to add details to your request if needed" maxlength="2000"></textarea>
      </div>
      <button class="ui submit button" type="submit">{{ $t('Submit') }}</button>
    </form>
    <div v-else class="ui success message">
      <div class="header">Request submitted!</div>
      <p>{{ $t('We\'ve received your request, you\'ll get some groove soon ;)') }}</p>
      <button @click="reset" class="ui button">{{ $t('Submit another request') }}</button>
    </div>
    <div v-if="requests.length > 0">
      <div class="ui divider"></div>
      <h3 class="ui header">{{ $t('Pending requests') }}</h3>
      <div class="ui list">
        <div v-for="request in requests" class="item">
          <div class="content">
            <div class="header">{{ request.artist_name }}</div>
            <div v-if="request.albums" class="description">
              {{ request.albums|truncate }}</div>
            <div v-if="request.comment" class="description">
              {{ request.comment|truncate }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import $ from 'jquery'
import axios from 'axios'

import logger from '@/logging'

export default {
  props: {
    defaultArtistName: {type: String, default: ''},
    defaultAlbums: {type: String, default: ''},
    defaultComment: {type: String, default: ''}
  },
  created () {
    this.fetchRequests()
  },
  mounted () {
    $('.ui.radio.checkbox').checkbox()
  },
  data () {
    return {
      currentArtistName: this.defaultArtistName,
      currentAlbums: this.defaultAlbums,
      currentComment: this.defaultComment,
      isLoading: false,
      over: false,
      requests: []
    }
  },
  methods: {
    fetchRequests () {
      let self = this
      let url = 'requests/import-requests/'
      axios.get(url, {}).then((response) => {
        self.requests = response.data.results
      })
    },
    submit () {
      let self = this
      this.isLoading = true
      let url = 'requests/import-requests/'
      let payload = {
        artist_name: this.currentArtistName,
        albums: this.currentAlbums,
        comment: this.currentComment
      }
      axios.post(url, payload).then((response) => {
        logger.default.info('Submitted request!')
        self.isLoading = false
        self.over = true
        self.requests.unshift(response.data)
      }, (response) => {
        logger.default.error('error while submitting request')
        self.isLoading = false
      })
    },
    reset () {
      this.over = false
      this.currentArtistName = ''
      this.currentAlbums = ''
      this.currentComment = ''
    },
    truncate (string, length) {
      if (string.length > length) {
        return string.substring(0, length) + '…'
      }
      return string
    }
  }
}
</script>

<style scoped>
</style>
