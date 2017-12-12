// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import logger from '@/logging'

logger.default.info('Loading environment:', process.env.NODE_ENV)
logger.default.debug('Environment variables:', process.env)

import Vue from 'vue'
import App from './App'
import router from './router'
import VueResource from 'vue-resource'
import auth from './auth'
import VueLazyload from 'vue-lazyload'

window.$ = window.jQuery = require('jquery')

// this is absolutely dirty but at the moment, semantic UI does not
// play really nice with webpack and I want to get rid of Google Fonts
// require('./semantic/semantic.css')
require('semantic-ui-css/semantic.js')

Vue.use(VueResource)
Vue.use(VueLazyload)
Vue.config.productionTip = false

Vue.http.interceptors.push(function (request, next) {
  // modify headers
  if (auth.user.authenticated) {
    request.headers.set('Authorization', auth.getAuthHeader())
  }
  next(function (response) {
    // redirect to login form when we get unauthorized response from server
    if (response.status === 401) {
      logger.default.warn('Received 401 response from API, redirecting to login form')
      router.push({name: 'login'})
    }
  })
})

auth.checkAuth()
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App }
})

logger.default.info('Everything loaded!')
