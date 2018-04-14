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
import i18next from 'i18next'
import i18nextFetch from 'i18next-fetch-backend'
import VueI18Next from '@panter/vue-i18next'
import store from './store'
import config from './config'
import { sync } from 'vuex-router-sync'
import filters from '@/filters' // eslint-disable-line
import globals from '@/components/globals' // eslint-disable-line

sync(store, router)

window.$ = window.jQuery = require('jquery')

// this is absolutely dirty but at the moment, semantic UI does not
// play really nice with webpack and I want to get rid of Google Fonts
// require('./semantic/semantic.css')
require('semantic-ui-css/semantic.js')
require('masonry-layout')

Vue.use(VueI18Next)
Vue.use(VueMasonryPlugin)
Vue.use(VueLazyload)
Vue.config.productionTip = false
Vue.directive('title', {
  inserted: (el, binding) => { console.log(binding.value); document.title = binding.value + ' - Funkwhale' },
  updated: (el, binding) => { document.title = binding.value + ' - Funkwhale' }
})

axios.defaults.baseURL = config.API_URL
axios.interceptors.request.use(function (config) {
  // Do something before request is sent
  if (store.state.auth.authenticated) {
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
    logger.default.warn('Received 401 response from API, redirecting to login form')
    router.push({name: 'login', query: {next: router.currentRoute.fullPath}})
  }
  if (error.response.status === 404) {
    error.backendErrors.push('Resource not found')
  } else if (error.response.status === 500) {
    error.backendErrors.push('A server error occured')
  } else if (error.response.data) {
    for (var field in error.response.data) {
      if (error.response.data.hasOwnProperty(field)) {
        error.response.data[field].forEach(e => {
          error.backendErrors.push(e)
        })
      }
    }
  }
  if (error.backendErrors.length === 0) {
    error.backendErrors.push(i18next.t('An unknown error occured, ensure your are connected to the internet and your funkwhale instance is up and running'))
  }
  // Do something with response error
  return Promise.reject(error)
})
store.dispatch('auth/check')

// i18n
i18next
  .use(i18nextFetch)
  .init({
    lng: navigator.language,
    fallbackLng: ['en'],
    preload: [navigator.language, 'en'],
    backend: {
      loadPath: '/static/translations/{%lng%}.json'
    },
    interpolation: {
      prefix: '{%',
      suffix: '%}'
    }
  })
const i18n = new VueI18Next(i18next)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  i18n,
  template: '<App/>',
  components: { App }
})

logger.default.info('Everything loaded!')
