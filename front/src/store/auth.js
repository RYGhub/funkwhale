import axios from 'axios'
import jwtDecode from 'jwt-decode'
import logger from '@/logging'
import router from '@/router'

export default {
  namespaced: true,
  state: {
    authenticated: false,
    username: '',
    availablePermissions: {},
    profile: null,
    token: '',
    tokenData: {}
  },
  getters: {
    header: state => {
      return 'JWT ' + state.token
    }
  },
  mutations: {
    reset (state) {
      state.authenticated = false
      state.profile = null
      state.username = ''
      state.token = ''
      state.tokenData = {}
      state.availablePermissions = {
        federation: false,
        library: false,
        upload: false
      }
    },
    profile: (state, value) => {
      state.profile = value
    },
    authenticated: (state, value) => {
      state.authenticated = value
      if (value === false) {
        state.username = null
        state.token = null
        state.tokenData = null
        state.profile = null
        state.availablePermissions = {}
      }
    },
    username: (state, value) => {
      state.username = value
    },
    avatar: (state, value) => {
      if (state.profile) {
        state.profile.avatar = value
      }
    },
    token: (state, value) => {
      state.token = value
      if (value) {
        state.tokenData = jwtDecode(value)
      } else {
        state.tokenData = {}
      }
    },
    permission: (state, {key, status}) => {
      state.availablePermissions[key] = status
    }
  },
  actions: {
    // Send a request to the login URL and save the returned JWT
    login ({commit, dispatch}, {next, credentials, onError}) {
      return axios.post('token/', credentials).then(response => {
        logger.default.info('Successfully logged in as', credentials.username)
        commit('token', response.data.token)
        dispatch('fetchProfile')
        // Redirect to a specified route
        router.push(next)
      }, response => {
        logger.default.error('Error while logging in', response.data)
        onError(response)
      })
    },
    logout ({commit}) {
      let modules = [
        'auth',
        'favorites',
        'player',
        'playlists',
        'queue',
        'radios'
      ]
      modules.forEach(m => {
        commit(`${m}/reset`, null, {root: true})
      })
      logger.default.info('Log out, goodbye!')
      router.push({name: 'index'})
    },
    check ({commit, dispatch, state}) {
      logger.default.info('Checking authentication...')
      var jwt = state.token
      if (jwt) {
        commit('token', jwt)
        dispatch('fetchProfile')
        dispatch('refreshToken')
      } else {
        logger.default.info('Anonymous user')
        commit('authenticated', false)
      }
    },
    fetchProfile ({commit, dispatch, state}) {
      if (document) {
        // this is to ensure we do not have any leaking cookie set by django
        document.cookie = 'sessionid=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
      }

      return axios.get('users/users/me/').then((response) => {
        logger.default.info('Successfully fetched user profile')
        let data = response.data
        commit('authenticated', true)
        commit('profile', data)
        commit('username', data.username)
        dispatch('favorites/fetch', null, { root: true })
        dispatch('playlists/fetchOwn', null, { root: true })
        Object.keys(data.permissions).forEach(function (key) {
          // this makes it easier to check for permissions in templates
          commit('permission', {key, status: data.permissions[String(key)]})
        })
        return response.data
      }, (response) => {
        logger.default.info('Error while fetching user profile')
      })
    },
    refreshToken ({commit, dispatch, state}) {
      return axios.post('token/refresh/', {token: state.token}).then(response => {
        logger.default.info('Refreshed auth token')
        commit('token', response.data.token)
      }, response => {
        logger.default.error('Error while refreshing token', response.data)
      })
    }
  }
}
