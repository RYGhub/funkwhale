import Vue from 'vue'
import Vuex from 'vuex'

import queue from './queue'
import radios from './radios'
import player from './player'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    queue,
    radios,
    player
  }
})
