import logger from '@/logging'
import _ from 'lodash'

export default {
  namespaced: true,
  state: {
    tracks: [],
    currentIndex: -1,
    ended: true,
    previousQueue: null
  },
  mutations: {
    currentIndex (state, value) {
      state.currentIndex = value
    },
    ended (state, value) {
      state.ended = value
    },
    splice (state, {start, size}) {
      state.tracks.splice(start, size)
    },
    tracks (state, value) {
      state.tracks = value
    },
    insert (state, {track, index}) {
      state.tracks.splice(index, 0, track)
    },
    reorder (state, {oldIndex, newIndex}) {
      // called when the user uses drag / drop to reorder
      // tracks in queue
      if (oldIndex === state.currentIndex) {
        state.currentIndex = newIndex
        return
      }
      if (oldIndex < state.currentIndex && newIndex >= state.currentIndex) {
        // item before was moved after
        state.currentIndex -= 1
      }
      if (oldIndex > state.currentIndex && newIndex <= state.currentIndex) {
        // item after was moved before
        state.currentIndex += 1
      }
    }

  },
  getters: {
    currentTrack: state => {
      return state.tracks[state.currentIndex]
    },
    hasNext: state => {
      return state.currentIndex < state.tracks.length - 1
    },
    hasPrevious: state => {
      return state.currentIndex > 0
    }
  },
  actions: {
    append (context, {track, index, skipPlay}) {
      index = index || context.state.tracks.length
      if (index > context.state.tracks.length - 1) {
        // we simply push to the end
        context.commit('insert', {track, index: context.state.tracks.length})
      } else {
        // we insert the track at given position
        context.commit('insert', {track, index})
      }
      if (!skipPlay) {
        context.dispatch('resume')
      }
      // this.cache()
    },

    appendMany (context, {tracks, index}) {
      logger.default.info('Appending many tracks to the queue', tracks.map(e => { return e.title }))
      if (context.state.tracks.length === 0) {
        index = 0
      } else {
        index = index || context.state.tracks.length
      }
      tracks.forEach((t) => {
        context.dispatch('append', {track: t, index: index, skipPlay: true})
        index += 1
      })
      context.dispatch('resume')
    },

    cleanTrack ({state, dispatch, commit}, index) {
      // are we removing current playin track
      let current = index === state.currentIndex
      if (current) {
        dispatch('player/stop', null, {root: true})
      }
      if (index < state.currentIndex) {
        dispatch('currentIndex', state.currentIndex - 1)
      }
      commit('splice', {start: index, size: 1})
      if (current) {
        // we play next track, which now have the same index
        dispatch('currentIndex', index)
      }
    },

    resume (context) {
      if (context.state.ended | context.rootState.player.errored) {
        context.dispatch('next')
      }
    },
    previous (context) {
      if (context.state.currentIndex > 0) {
        context.dispatch('currentIndex', context.state.currentIndex - 1)
      }
    },
    next ({state, dispatch, commit, rootState}) {
      if (rootState.player.looping === 1) {
        // we loop on the same track, this is handled directly on the track
        // component, so we do nothing.
        return logger.default.info('Looping on the same track')
      }
      if (rootState.player.looping === 2 && state.currentIndex >= state.tracks.length - 1) {
        logger.default.info('Going back to the beginning of the queue')
        return dispatch('currentIndex', 0)
      } else {
        if (state.currentIndex < state.tracks.length - 1) {
          logger.default.debug('Playing next track')
          return dispatch('currentIndex', state.currentIndex + 1)
        } else {
          commit('ended', true)
        }
      }
    },
    currentIndex ({commit, state, rootState, dispatch}, index) {
      commit('ended', false)
      commit('player/errored', false, {root: true})
      commit('currentIndex', index)
      if (state.tracks.length - index <= 2 && rootState.radios.running) {
        dispatch('radios/populateQueue', null, {root: true})
      }
    },
    clean ({dispatch, commit}) {
      dispatch('player/stop', null, {root: true})
      // radios.stop()
      commit('tracks', [])
      dispatch('currentIndex', -1)
      // so we replay automatically on next track append
      commit('ended', true)
    },
    shuffle ({dispatch, commit, state}) {
      let shuffled = _.shuffle(state.tracks)
      commit('tracks', [])
      dispatch('appendMany', {tracks: shuffled})
    }
  }
}
