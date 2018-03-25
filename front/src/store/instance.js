import axios from 'axios'
import logger from '@/logging'
import _ from 'lodash'

export default {
  namespaced: true,
  state: {
    maxEvents: 200,
    events: [],
    settings: {
      instance: {
        name: {
          value: ''
        },
        short_description: {
          value: ''
        },
        long_description: {
          value: ''
        }
      },
      users: {
        registration_enabled: {
          value: true
        }
      },
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
    },
    event: (state, value) => {
      state.events.unshift(value)
      if (state.events.length > state.maxEvents) {
        state.events = state.events.slice(0, state.maxEvents)
      }
    },
    events: (state, value) => {
      state.events = value
    }
  },
  actions: {
    // Send a request to the login URL and save the returned JWT
    fetchSettings ({commit}, payload) {
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
        if (payload && payload.callback) {
          payload.callback()
        }
      }, response => {
        logger.default.error('Error while fetching settings', response.data)
      })
    }
  }
}
