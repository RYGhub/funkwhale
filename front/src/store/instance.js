import axios from 'axios'
import logger from '@/logging'
import _ from 'lodash'

export default {
  namespaced: true,
  state: {
    settings: {
      raven: {
        front_enabled: {
          value: false
        },
        front_dsn: {
          value: null
        }
      }
    }
  },
  mutations: {
    settings: (state, value) => {
      _.merge(state.settings, value)
    }
  },
  actions: {
    // Send a request to the login URL and save the returned JWT
    fetchSettings ({commit}) {
      return axios.get('instance/settings/').then(response => {
        logger.default.info('Successfully fetched instance settings')
        let sections = {}
        response.data.forEach(e => {
          sections[e.section] = {}
        })
        response.data.forEach(e => {
          sections[e.section][e.name] = e
        })
        commit('settings', sections)
      }, response => {
        logger.default.error('Error while fetching settings', response.data)
      })
    }
  }
}
