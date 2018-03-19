import axios from 'axios'

export default {
  namespaced: true,
  state: {
    playlists: []
  },
  mutations: {
    playlists (state, value) {
      state.playlists = value
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
