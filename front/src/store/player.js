import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'
import time from '@/utils/time'

export default {
  namespaced: true,
  state: {
    playing: false,
    volume: 0.5,
    duration: 0,
    currentTime: 0,
    errored: false,
    looping: 0 // 0 -> no, 1 -> on  track, 2 -> on queue
  },
  mutations: {
    volume (state, value) {
      value = parseFloat(value)
      value = Math.min(value, 1)
      value = Math.max(value, 0)
      state.volume = value
    },
    incrementVolume (state, value) {
      value = parseFloat(state.volume + value)
      value = Math.min(value, 1)
      value = Math.max(value, 0)
      state.volume = value
    },
    duration (state, value) {
      state.duration = value
    },
    errored (state, value) {
      state.errored = value
    },
    currentTime (state, value) {
      state.currentTime = value
    },
    looping (state, value) {
      state.looping = value
    },
    playing (state, value) {
      state.playing = value
    },
    toggleLooping (state) {
      if (state.looping > 1) {
        state.looping = 0
      } else {
        state.looping += 1
      }
    }
  },
  getters: {
    durationFormatted: state => {
      return time.parse(Math.round(state.duration))
    },
    currentTimeFormatted: state => {
      return time.parse(Math.round(state.currentTime))
    },
    progress: state => {
      return Math.round(state.currentTime / state.duration * 100)
    }
  },
  actions: {
    incrementVolume ({commit, state}, value) {
      commit('volume', state.volume + value)
    },
    stop (context) {
    },
    togglePlay ({commit, state}) {
      commit('playing', !state.playing)
    },
    trackListened ({commit}, track) {
      let url = config.API_URL + 'history/listenings/'
      let resource = Vue.resource(url)
      resource.save({}, {'track': track.id}).then((response) => {}, (response) => {
        logger.default.error('Could not record track in history')
      })
    },
    trackEnded ({dispatch}, track) {
      dispatch('trackListened', track)
      dispatch('queue/next', null, {root: true})
    },
    trackErrored ({commit, dispatch}) {
      commit('errored', true)
      dispatch('queue/next', null, {root: true})
    },
    updateProgress ({commit}, t) {
      commit('currentTime', t)
    }
  }
}
