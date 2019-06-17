import axios from 'axios'
import moment from 'moment'

export default {
  namespaced: true,
  state: {
    currentLanguage: 'en_US',
    momentLocale: 'en',
    lastDate: new Date(),
    maxMessages: 100,
    messageDisplayDuration: 10000,
    messages: [],
    theme: 'light',
    notifications: {
      inbox: 0,
      pendingReviewEdits: 0,
    },
    websocketEventsHandlers: {
      'inbox.item_added': {},
      'import.status_updated': {},
      'mutation.created': {},
      'mutation.updated': {},
    },
    pageTitle: null
  },
  mutations: {
    addWebsocketEventHandler: (state, {eventName, id, handler}) => {
      state.websocketEventsHandlers[eventName][id] = handler
    },
    removeWebsocketEventHandler: (state, {eventName, id}) => {
      delete state.websocketEventsHandlers[eventName][id]
    },
    currentLanguage: (state, value) => {
      state.currentLanguage = value
    },
    momentLocale: (state, value) => {
      state.momentLocale = value
      moment.locale(value)
    },
    computeLastDate: (state) => {
      state.lastDate = new Date()
    },
    theme: (state, value) => {
      state.theme = value
    },
    addMessage (state, message) {
      state.messages.push(message)
      if (state.messages.length > state.maxMessages) {
        state.messages.shift()
      }
    },
    notifications (state, {type, count}) {
      state.notifications[type] = count
    },
    incrementNotifications (state, {type, count, value}) {
      if (value != undefined) {
          state.notifications[type] = Math.max(0, value)
      } else {
        state.notifications[type] = Math.max(0, state.notifications[type] + count)
      }
    },
    pageTitle: (state, value) => {
      state.pageTitle = value
    }
  },
  actions: {
    fetchUnreadNotifications ({commit}, payload) {
      axios.get('federation/inbox/', {params: {is_read: false, page_size: 1}}).then((response) => {
        commit('notifications', {type: 'inbox', count: response.data.count})
      })
    },
    fetchPendingReviewEdits ({commit, rootState}, payload) {
      axios.get('mutations/', {params: {is_approved: 'null', page_size: 1}}).then((response) => {
        commit('notifications', {type: 'pendingReviewEdits', count: response.data.count})
      })
    },
    websocketEvent ({state}, event) {
      let handlers = state.websocketEventsHandlers[event.type]
      console.log('Dispatching websocket event', event, handlers)
      if (!handlers) {
        return
      }
      let names = Object.keys(handlers)
      names.forEach((k) => {
        let handler = handlers[k]
        handler(event)
      })
    }
  }
}
