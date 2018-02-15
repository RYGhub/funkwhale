// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import logger from '@/logging'

logger.default.info('Loading environment:', process.env.NODE_ENV)
logger.default.debug('Environment variables:', process.env)

import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import VueLazyload from 'vue-lazyload'
import store from './store'
import config from './config'
import { sync } from 'vuex-router-sync'

sync(store, router)

window.$ = window.jQuery = require('jquery')

// this is absolutely dirty but at the moment, semantic UI does not
// play really nice with webpack and I want to get rid of Google Fonts
// require('./semantic/semantic.css')
require('semantic-ui-css/semantic.js')

Vue.use(VueLazyload)
Vue.config.productionTip = false

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
  if (response.status === 401) {
    store.commit('auth/authenticated', false)
    logger.default.warn('Received 401 response from API, redirecting to login form')
    router.push({name: 'login', query: {next: router.currentRoute.fullPath}})
  }
  return response
}, function (error) {
  // Do something with response error
  return Promise.reject(error)
})
store.dispatch('auth/check')
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  components: { App }
})

logger.default.info('Everything loaded!')
