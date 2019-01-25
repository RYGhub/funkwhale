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
    notifications: {
      inbox: 0,
    },
    websocketEventsHandlers: {
      'inbox.item_added': {},
      'import.status_updated': {},
    }
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
    addMessage (state, message) {
      state.messages.push(message)
      if (state.messages.length > state.maxMessages) {
        state.messages.shift()
      }
    },
    notifications (state, {type, count}) {
      state.notifications[type] = count
    },
    incrementNotifications (state, {type, count}) {
      state.notifications[type] = Math.max(0, state.notifications[type] + count)
    }
  },
  actions: {
    fetchUnreadNotifications ({commit}, payload) {
      axios.get('federation/inbox/', {params: {is_read: false, page_size: 1}}).then((response) => {
        commit('notifications', {type: 'inbox', count: response.data.count})
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
