
export default {
  namespaced: true,
  state: {
    lastDate: new Date()
  },
  mutations: {
    computeLastDate: (state) => {
      state.lastDate = new Date()
    }
  }
}
