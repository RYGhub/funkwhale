import axios from 'axios'
import moment from 'moment'

export default {
  namespaced: true,
  state: {
    currentLanguage: 'en_US',
    selectedLanguage: false,
    momentLocale: 'en',
    lastDate: new Date(),
    maxMessages: 100,
    messageDisplayDuration: 10000,
    messages: [],
    theme: 'light',
    notifications: {
      inbox: 0,
      pendingReviewEdits: 0,
      pendingReviewReports: 0,
    },
    websocketEventsHandlers: {
      'inbox.item_added': {},
      'import.status_updated': {},
      'mutation.created': {},
      'mutation.updated': {},
      'report.created': {},
    },
    pageTitle: null,
    routePreferences: {
      "library.albums.browse": {
        paginateBy: 25,
        orderingDirection: "-",
        ordering: "creation_date",
      },
      "library.artists.browse": {
        paginateBy: 30,
        orderingDirection: "-",
        ordering: "creation_date",
      },
      "library.radios.browse": {
        paginateBy: 12,
        orderingDirection: "-",
        ordering: "creation_date",
      },
      "library.playlists.browse": {
        paginateBy: 25,
        orderingDirection: "-",
        ordering: "creation_date",
      },
    },
  },
  getters: {
    showInstanceSupportMessage: (state, getters, rootState) => {
      if (!rootState.auth.profile) {
        return false
      }
      if (!rootState.instance.settings.instance.support_message.value) {
        return false
      }
      let displayDate = rootState.auth.profile.instance_support_message_display_date
      if (!displayDate) {
        return false
      }
      return moment(displayDate) < moment(state.lastDate)
    },
    showFunkwhaleSupportMessage: (state, getters, rootState) => {
      if (!rootState.auth.profile) {
        return false
      }
      if (!rootState.instance.settings.instance.funkwhale_support_message_enabled.value) {
        return false
      }
      let displayDate = rootState.auth.profile.funkwhale_support_message_display_date
      if (!displayDate) {
        return false
      }
      return moment(displayDate) < moment(state.lastDate)
    },
    additionalNotifications: (state, getters) => {
      let count = 0
      if (getters.showInstanceSupportMessage) {
        count += 1
      }
      if (getters.showFunkwhaleSupportMessage) {
        count += 1
      }
      return count
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
      state.selectedLanguage = true
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
    },
    paginateBy: (state, {route, value}) => {
      state.routePreferences[route].paginateBy = value
    },
    ordering: (state, {route, value}) => {
      state.routePreferences[route].ordering = value
    },
    orderingDirection: (state, {route, value}) => {
      state.routePreferences[route].orderingDirection = value
    },
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
    fetchPendingReviewReports ({commit, rootState}, payload) {
      axios.get('manage/moderation/reports/', {params: {is_handled: 'false', page_size: 1}}).then((response) => {
        commit('notifications', {type: 'pendingReviewReports', count: response.data.count})
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
