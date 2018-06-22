import axios from 'axios'

export default {
  namespaced: true,
  state: {
    lastDate: new Date(),
    maxMessages: 100,
    messageDisplayDuration: 10000,
    messages: [],
    notifications: {
      federation: 0,
      importRequests: 0
    }
  },
  mutations: {
    computeLastDate: (state) => {
      state.lastDate = new Date()
    },
    addMessage (state, message) {
      state.messages.push(message)
      if (state.messages.length > state.maxMessages) {
        state.messages.shift()
      }
    },
    notifications (state, {type, count}) {
      state.notifications[type] = count
    }
  },
  actions: {
    fetchFederationNotificationsCount ({rootState, commit}) {
      if (!rootState.auth.availablePermissions['federation']) {
        return
      }
      axios.get('federation/libraries/followers/', {params: {pending: true}}).then(response => {
        commit('notifications', {type: 'federation', count: response.data.count})
      })
    },
    fetchImportRequestsCount ({rootState, commit}) {
      if (!rootState.auth.availablePermissions['library']) {
        return
      }
      axios.get('requests/import-requests/', {params: {status: 'pending'}}).then(response => {
        commit('notifications', {type: 'importRequests', count: response.data.count})
      })
    }
  }
}
