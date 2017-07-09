import logger from '@/logging'
import config from '@/config'
import cache from '@/cache'
import Vue from 'vue'

import favoriteTracks from '@/favorites/tracks'

// URL and endpoint constants
const LOGIN_URL = config.API_URL + 'token/'
const USER_PROFILE_URL = config.API_URL + 'users/users/me/'
// const SIGNUP_URL = API_URL + 'users/'

let userData = {
  authenticated: false,
  username: '',
  availablePermissions: {},
  profile: {}
}
let auth = {

  // Send a request to the login URL and save the returned JWT
  login (context, creds, redirect, onError) {
    return context.$http.post(LOGIN_URL, creds).then(response => {
      logger.default.info('Successfully logged in as', creds.username)
      cache.set('token', response.data.token)
      cache.set('username', creds.username)

      this.user.authenticated = true
      this.user.username = creds.username
      this.connect()
      // Redirect to a specified route
      if (redirect) {
        context.$router.push(redirect)
      }
    }, response => {
      logger.default.error('Error while logging in', response.data)
      if (onError) {
        onError(response)
      }
    })
  },

  // To log out, we just need to remove the token
  logout () {
    cache.clear()
    this.user.authenticated = false
    logger.default.info('Log out, goodbye!')
  },

  checkAuth () {
    logger.default.info('Checking authentication...')
    var jwt = this.getAuthToken()
    var username = cache.get('username')
    if (jwt) {
      this.user.authenticated = true
      this.user.username = username
      logger.default.info('Logged back in as ' + username)
      this.connect()
    } else {
      logger.default.info('Anonymous user')
      this.user.authenticated = false
    }
  },

  getAuthToken () {
    return cache.get('token')
  },

  // The object to be passed as a header for authenticated requests
  getAuthHeader () {
    return 'JWT ' + this.getAuthToken()
  },

  fetchProfile () {
    let resource = Vue.resource(USER_PROFILE_URL)
    return resource.get({}).then((response) => {
      logger.default.info('Successfully fetched user profile')
      return response.data
    }, (response) => {
      logger.default.info('Error while fetching user profile')
    })
  },
  connect () {
    // called once user has logged in successfully / reauthenticated
    // e.g. after a page refresh
    let self = this
    this.fetchProfile().then(data => {
      Vue.set(self.user, 'profile', data)
      Object.keys(data.permissions).forEach(function (key) {
        // this makes it easier to check for permissions in templates
        Vue.set(self.user.availablePermissions, key, data.permissions[String(key)].status)
      })
    })
    favoriteTracks.fetch()
  }
}

Vue.set(auth, 'user', userData)
export default auth
