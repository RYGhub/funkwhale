// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import logger from '@/logging'

logger.default.info('Loading environment:', process.env.NODE_ENV)
logger.default.debug('Environment variables:', process.env)

import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import {VueMasonryPlugin} from 'vue-masonry'
import VueLazyload from 'vue-lazyload'
import store from './store'
import GetTextPlugin from 'vue-gettext'
import { sync } from 'vuex-router-sync'
import locales from '@/locales'

import filters from '@/filters' // eslint-disable-line
import globals from '@/components/globals' // eslint-disable-line

sync(store, router)

window.$ = window.jQuery = require('jquery')
require('./semantic.js')
require('masonry-layout')

let availableLanguages = (function () {
  let l = {}
  locales.locales.forEach(c => {
    l[c.code] = c.label
  })
  return l
})()
let defaultLanguage = 'en_US'
if (availableLanguages[store.state.ui.currentLanguage]) {
  defaultLanguage = store.state.ui.currentLanguage
}
Vue.use(GetTextPlugin, {
  availableLanguages: availableLanguages,
  defaultLanguage: defaultLanguage,
  // cf https://github.com/Polyconseil/vue-gettext#configuration
  // not recommended but this is fixing weird bugs with translation nodes
  // not being updated when in v-if/v-else clauses
  autoAddKeyAttributes: true,
  languageVmMixin: {
    computed: {
      currentKebabCase: function () {
        return this.current.toLowerCase().replace('_', '-')
      }
    }
  },
  translations: {},
  silent: true
})

Vue.use(VueMasonryPlugin)
Vue.use(VueLazyload)
Vue.config.productionTip = false
Vue.directive('title', {
  inserted: (el, binding) => {
    let parts = []
    let instanceName = store.state.instance.settings.instance.name.value
    if (instanceName.length === 0) {
      instanceName = 'Funkwhale'
    }
    parts.unshift(instanceName)
    parts.unshift(binding.value)
    document.title = parts.join(' - ')
  },
  updated: (el, binding) => {
    let parts = []
    let instanceName = store.state.instance.settings.instance.name.value
    if (instanceName.length === 0) {
      instanceName = 'Funkwhale'
    }
    parts.unshift(instanceName)
    parts.unshift(binding.value)
    document.title = parts.join(' - ')
  }
})
axios.interceptors.request.use(function (config) {
  // Do something before request is sent
  if (store.state.auth.token) {
    config.headers['Authorization'] = store.getters['auth/header']
  }
  return config
}, function (error) {
  // Do something with request error
  return Promise.reject(error)
})

// Add a response interceptor
axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  error.backendErrors = []
  if (error.response.status === 401) {
    store.commit('auth/authenticated', false)
    logger.default.warn('Received 401 response from API, redirecting to login form', router.currentRoute.fullPath)
    router.push({name: 'login', query: {next: router.currentRoute.fullPath}})
  }
  if (error.response.status === 404) {
    error.backendErrors.push('Resource not found')
  } else if (error.response.status === 403) {
    error.backendErrors.push('Permission denied')
  } else if (error.response.status === 500) {
    error.backendErrors.push('A server error occured')
  } else if (error.response.data) {
    if (error.response.data.detail) {
      error.backendErrors.push(error.response.data.detail)
    } else {
      for (var field in error.response.data) {
        if (error.response.data.hasOwnProperty(field)) {
          error.response.data[field].forEach(e => {
            error.backendErrors.push(e)
          })
        }
      }
    }
  }
  if (error.backendErrors.length === 0) {
    error.backendErrors.push('An unknown error occured, ensure your are connected to the internet and your funkwhale instance is up and running')
  }
  // Do something with response error
  return Promise.reject(error)
})

store.dispatch('instance/fetchFrontSettings').finally(() => {
  /* eslint-disable no-new */
  new Vue({
    el: '#app',
    router,
    store,
    template: '<App/>',
    components: { App }
  })

  logger.default.info('Everything loaded!')
})
