import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'
import cache from '@/cache'
import router from '@/router'

const LOGIN_URL = config.API_URL + 'token/'
const USER_PROFILE_URL = config.API_URL + 'users/users/me/'

export default {
  namespaced: true,
  state: {
    authenticated: false,
    username: '',
    availablePermissions: {},
    profile: null,
    token: ''
  },
  getters: {
    header: state => {
      return 'JWT ' + state.token
    }
  },
  mutations: {
    profile: (state, value) => {
      state.profile = value
    },
    authenticated: (state, value) => {
      state.authenticated = value
    },
    username: (state, value) => {
      state.username = value
    },
    token: (state, value) => {
      state.token = value
    },
    permission: (state, {key, status}) => {
      state.availablePermissions[key] = status
    }
  },
  actions: {
    // Send a request to the login URL and save the returned JWT
    login ({commit, dispatch, state}, {next, credentials, onError}) {
      let resource = Vue.resource(LOGIN_URL)
      return resource.save({}, credentials).then(response => {
        logger.default.info('Successfully logged in as', credentials.username)
        commit('token', response.data.token)
        cache.set('token', response.data.token)
        commit('username', credentials.username)
        cache.set('username', credentials.username)
        commit('authenticated', true)
        dispatch('fetchProfile')
        // Redirect to a specified route
        router.push(next)
      }, response => {
        logger.default.error('Error while logging in', response.data)
        onError(response)
      })
    },
    logout ({commit}) {
      cache.clear()
      commit('authenticated', false)
      commit('profile', null)
      logger.default.info('Log out, goodbye!')
      router.push({name: 'index'})
    },
    check ({commit, dispatch, state}) {
      logger.default.info('Checking authentication...')
      var jwt = cache.get('token')
      var username = cache.get('username')
      if (jwt) {
        commit('authenticated', true)
        commit('username', username)
        commit('token', jwt)
        logger.default.info('Logged back in as ' + username)
        dispatch('fetchProfile')
      } else {
        logger.default.info('Anonymous user')
        commit('authenticated', false)
      }
    },
    fetchProfile ({commit, dispatch, state}) {
      let resource = Vue.resource(USER_PROFILE_URL)
      return resource.get({}).then((response) => {
        logger.default.info('Successfully fetched user profile')
        let data = response.data
        commit('profile', data)
        dispatch('favorites/fetch', null, {root: true})
        Object.keys(data.permissions).forEach(function (key) {
          // this makes it easier to check for permissions in templates
          commit('permission', {key, status: data.permissions[String(key)].status})
        })
        return response.data
      }, (response) => {
        logger.default.info('Error while fetching user profile')
      })
    }
  }
}
