
export default {
  namespaced: true,
  state: {
    lastDate: new Date(),
    maxMessages: 100,
    messageDisplayDuration: 10000,
    messages: []
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
    }
  }
}
