import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'

const CREATE_RADIO_URL = config.API_URL + 'radios/sessions/'
const GET_TRACK_URL = config.API_URL + 'radios/tracks/'

export default {
  namespaced: true,
  state: {
    current: null,
    running: false
  },
  getters: {
    types: state => {
      return {
        random: {
          name: 'Random',
          description: "Totally random picks, maybe you'll discover new things?"
        },
        favorites: {
          name: 'Favorites',
          description: 'Play your favorites tunes in a never-ending happiness loop.'
        },
        'less-listened': {
          name: 'Less listened',
          description: "Listen to tracks you usually don't. It's time to restore some balance."
        }
      }
    }
  },
  mutations: {
    current: (state, value) => {
      state.current = value
    },
    running: (state, value) => {
      state.running = value
    }
  },
  actions: {
    start ({commit, dispatch}, {type, objectId}) {
      let resource = Vue.resource(CREATE_RADIO_URL)
      var params = {
        radio_type: type,
        related_object_id: objectId
      }
      resource.save({}, params).then((response) => {
        logger.default.info('Successfully started radio ', type)
        commit('current', {type, objectId, session: response.data.id})
        commit('running', true)
        dispatch('populateQueue')
      }, (response) => {
        logger.default.error('Error while starting radio', type)
      })
    },
    stop ({commit}) {
      commit('current', null)
      commit('running', false)
    },
    populateQueue ({state, dispatch}) {
      if (!state.running) {
        return
      }
      let resource = Vue.resource(GET_TRACK_URL)
      var params = {
        session: state.current.session
      }
      let promise = resource.save({}, params)
      promise.then((response) => {
        logger.default.info('Adding track to queue from radio')
        dispatch('queue/append', {track: response.data.track}, {root: true})
      }, (response) => {
        logger.default.error('Error while adding track to queue from radio')
      })
    }
  }

}
