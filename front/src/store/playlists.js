import axios from 'axios'

export default {
  namespaced: true,
  state: {
    playlists: [],
    showModal: false,
    modalTrack: null
  },
  mutations: {
    playlists (state, value) {
      state.playlists = value
    },
    chooseTrack (state, value) {
      state.showModal = true
      state.modalTrack = value
    },
    showModal (state, value) {
      state.showModal = value
    }
  },
  actions: {
    fetchOwn ({commit, rootState}) {
      let userId = rootState.auth.profile.id
      if (!userId) {
        return
      }
      return axios.get('playlists/', {params: {user: userId}}).then((response) => {
        commit('playlists', response.data.results)
      })
    }
  }
}
