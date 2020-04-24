import axios from 'axios'
import logger from '@/logging'

export default {
  namespaced: true,
  state: {
    followedLibraries: [],
    followsByLibrary: {},
    count: 0,
  },
  mutations: {
    follows: (state, {library, follow}) => {
      let replacement = {...state.followsByLibrary}
      if (follow) {
        if (state.followedLibraries.indexOf(library) === -1) {
          state.followedLibraries.push(library)
          replacement[library] = follow
        }
      } else {
        let i = state.followedLibraries.indexOf(library)
        if (i > -1) {
          state.followedLibraries.splice(i, 1)
          replacement[library] = null
        }
      }
      state.followsByLibrary = replacement
      state.count = state.followedLibraries.length
    },
    reset (state) {
      state.followedLibraries = []
      state.followsByLibrary = {}
      state.count = 0
    },
  },
  getters: {
    follow: (state) => (library) => {
      return state.followsByLibrary[library]
    }
  },
  actions: {
    set ({commit, state}, {uuid, value}) {
      if (value) {
        return axios.post(`federation/follows/library/`, {target: uuid}).then((response) => {
          logger.default.info('Successfully subscribed to library')
          commit('follows', {library: uuid, follow: response.data})
        }, (response) => {
          logger.default.info('Error while subscribing to library')
          commit('follows', {library: uuid, follow: null})
        })
      } else {
        let follow = state.followsByLibrary[uuid]
        return axios.delete(`federation/follows/library/${follow.uuid}/`).then((response) => {
          logger.default.info('Successfully unsubscribed from library')
          commit('follows', {library: uuid, follow: null})
        }, (response) => {
          logger.default.info('Error while unsubscribing from library')
          commit('follows', {library: uuid, follow: follow})
        })
      }
    },
    toggle ({getters, dispatch}, uuid) {
      dispatch('set', {uuid, value: !getters['follow'](uuid)})
    },
    fetchFollows ({dispatch, state, commit, rootState}, url) {
      let promise = axios.get('federation/follows/library/all/')
      return promise.then((response) => {
        response.data.results.forEach(result => {
          commit('follows', {library: result.library, follow: result})
        })
      })
    }
  }
}
