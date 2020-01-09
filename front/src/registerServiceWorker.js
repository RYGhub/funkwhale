/* eslint-disable no-console */

import { register } from 'register-service-worker'

import store from './store'

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready (registration) {
      console.log(
        'App is being served from cache by a service worker.', registration
      )
      // check for updates every 2 hours
      var checkInterval = 1000 * 60 * 60 * 2
      // var checkInterval = 1000 * 5
      setInterval(() => {
        console.log('Checking for service worker update…')
        registration.update();
      }, checkInterval);
      store.commit('ui/serviceWorker', {registration: registration})
      if (registration.active) {
        registration.active.postMessage({command: 'serverChosen', serverUrl: store.state.instance.instanceUrl})
      }
    },
    registered () {
      console.log('Service worker has been registered.')
    },
    cached () {
      console.log('Content has been cached for offline use.')
    },
    updatefound () {
      console.log('New content is downloading.')
    },
    updated (registration) {
      console.log('New content is available; please refresh!')
      store.commit('ui/serviceWorker', {updateAvailable: true, registration: registration})
    },
    offline () {
      console.log('No internet connection found. App is running in offline mode.')
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })
}
