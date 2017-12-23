import Vue from 'vue'
import Vuex from 'vuex'

import favorites from './favorites'
import auth from './auth'
import queue from './queue'
import radios from './radios'
import player from './player'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth,
    favorites,
    queue,
    radios,
    player
  }
})
