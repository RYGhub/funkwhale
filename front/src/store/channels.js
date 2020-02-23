import axios from 'axios'
import logger from '@/logging'

export default {
  namespaced: true,
  state: {
    subscriptions: [],
    count: 0,
    showUploadModal: false,
    latestPublication: null,
    uploadModalConfig: {
      channel: null,
    }
  },
  mutations: {
    subscriptions: (state, {uuid, value}) => {
      if (value) {
        if (state.subscriptions.indexOf(uuid) === -1) {
          state.subscriptions.push(uuid)
        }
      } else {
        let i = state.subscriptions.indexOf(uuid)
        if (i > -1) {
          state.subscriptions.splice(i, 1)
        }
      }
      state.count = state.subscriptions.length
    },
    reset (state) {
      state.subscriptions = []
      state.count = 0
    },
    showUploadModal (state, value) {
      state.showUploadModal = value.show
      if (value.config) {
        state.uploadModalConfig = {
          ...value.config
        }
      }
    },
    publish (state, {uploads, channel}) {
      state.latestPublication = {
        date: new Date(),
        uploads,
        channel,
      }
      state.showUploadModal = false
    }
  },
  getters: {
    isSubscribed: (state) => (uuid) => {
      return state.subscriptions.indexOf(uuid) > -1
    }
  },
  actions: {
    set ({commit, state}, {uuid, value}) {
      commit('subscriptions', {uuid, value})
      if (value) {
        return axios.post(`channels/${uuid}/subscribe/`).then((response) => {
          logger.default.info('Successfully subscribed to channel')
        }, (response) => {
          logger.default.info('Error while subscribing to channel')
          commit('subscriptions', {uuid, value: !value})
        })
      } else {
        return axios.post(`channels/${uuid}/unsubscribe/`).then((response) => {
          logger.default.info('Successfully unsubscribed from channel')
        }, (response) => {
          logger.default.info('Error while unsubscribing from channel')
          commit('subscriptions', {uuid, value: !value})
        })
      }
    },
    toggle ({getters, dispatch}, uuid) {
      dispatch('set', {uuid, value: !getters['isSubscribed'](uuid)})
    },
    fetchSubscriptions ({dispatch, state, commit, rootState}, url) {
      let promise = axios.get('subscriptions/all/')
      return promise.then((response) => {
        response.data.results.forEach(result => {
          commit('subscriptions', {uuid: result.channel, value: true})
        })
      })
    }
  }
}
