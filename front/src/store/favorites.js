import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'

const REMOVE_URL = config.API_URL + 'favorites/tracks/remove/'
const FAVORITES_URL = config.API_URL + 'favorites/tracks/'

export default {
  namespaced: true,
  state: {
    tracks: [],
    count: 0
  },
  mutations: {
    track: (state, {id, value}) => {
      if (value) {
        state.tracks.push(id)
      } else {
        let i = state.tracks.indexOf(id)
        if (i > -1) {
          state.tracks.splice(i, 1)
        }
      }
    },
    count: (state, value) => {
      state.count = value
    }
  },
  getters: {
    isFavorite: (state) => (id) => {
      return state.tracks.indexOf(id) > -1
    }
  },
  actions: {
    set ({commit, state}, {id, value}) {
      commit('track', {id, value})
      if (value) {
        commit('count', state.count + 1)
        let resource = Vue.resource(FAVORITES_URL)
        resource.save({}, {'track': id}).then((response) => {
          logger.default.info('Successfully added track to favorites')
        }, (response) => {
          logger.default.info('Error while adding track to favorites')
          commit('track', {id, value: !value})
          commit('count', state.count - 1)
        })
      } else {
        commit('count', state.count - 1)
        let resource = Vue.resource(REMOVE_URL)
        resource.delete({}, {'track': id}).then((response) => {
          logger.default.info('Successfully removed track from favorites')
        }, (response) => {
          logger.default.info('Error while removing track from favorites')
          commit('track', {id, value: !value})
          commit('count', state.count + 1)
        })
      }
    },
    toggle ({getters, dispatch}, id) {
      dispatch('set', {id, value: getters['isFavorite'](id)})
    },
    fetch ({dispatch, state, commit}, url) {
      // will fetch favorites by batches from API to have them locally
      url = url || FAVORITES_URL
      let resource = Vue.resource(url)
      resource.get().then((response) => {
        logger.default.info('Fetched a batch of ' + response.data.results.length + ' favorites')
        response.data.results.forEach(result => {
          commit('track', {id: result.track, value: true})
        })
        commit('count', state.tracks.length)
        if (response.data.next) {
          dispatch('fetch', response.data.next)
        }
      })
    }
  }
}
