import store from '@/store/player'

import { testAction } from '../../utils'

describe('store/player', () => {
  describe('mutations', () => {
    it('set volume', () => {
      const state = { volume: 0 }
      store.mutations.volume(state, 0.9)
      expect(state.volume).to.equal(0.9)
    })
    it('set volume max 1', () => {
      const state = { volume: 0 }
      store.mutations.volume(state, 2)
      expect(state.volume).to.equal(1)
    })
    it('set volume min to 0', () => {
      const state = { volume: 0.5 }
      store.mutations.volume(state, -2)
      expect(state.volume).to.equal(0)
    })
    it('increment volume', () => {
      const state = { volume: 0 }
      store.mutations.incrementVolume(state, 0.1)
      expect(state.volume).to.equal(0.1)
    })
    it('increment volume max 1', () => {
      const state = { volume: 0 }
      store.mutations.incrementVolume(state, 2)
      expect(state.volume).to.equal(1)
    })
    it('increment volume min to 0', () => {
      const state = { volume: 0.5 }
      store.mutations.incrementVolume(state, -2)
      expect(state.volume).to.equal(0)
    })
    it('set duration', () => {
      const state = { duration: 42 }
      store.mutations.duration(state, 14)
      expect(state.duration).to.equal(14)
    })
    it('set errored', () => {
      const state = { errored: false }
      store.mutations.errored(state, true)
      expect(state.errored).to.equal(true)
    })
    it('set looping', () => {
      const state = { looping: 1 }
      store.mutations.looping(state, 2)
      expect(state.looping).to.equal(2)
    })
    it('set playing', () => {
      const state = { playing: false }
      store.mutations.playing(state, true)
      expect(state.playing).to.equal(true)
    })
    it('set current time', () => {
      const state = { currentTime: 1 }
      store.mutations.currentTime(state, 2)
      expect(state.currentTime).to.equal(2)
    })
    it('toggle looping from 0', () => {
      const state = { looping: 0 }
      store.mutations.toggleLooping(state)
      expect(state.looping).to.equal(1)
    })
    it('toggle looping from 1', () => {
      const state = { looping: 1 }
      store.mutations.toggleLooping(state)
      expect(state.looping).to.equal(2)
    })
    it('toggle looping from 2', () => {
      const state = { looping: 2 }
      store.mutations.toggleLooping(state)
      expect(state.looping).to.equal(0)
    })
    it('increment error count', () => {
      const state = { errorCount: 0 }
      store.mutations.incrementErrorCount(state)
      expect(state.errorCount).to.equal(1)
    })
    it('reset error count', () => {
      const state = { errorCount: 10 }
      store.mutations.resetErrorCount(state)
      expect(state.errorCount).to.equal(0)
    })
  })
  describe('getters', () => {
    it('durationFormatted', () => {
      const state = { duration: 12.51 }
      expect(store.getters['durationFormatted'](state)).to.equal('00:13')
    })
    it('currentTimeFormatted', () => {
      const state = { currentTime: 12.51 }
      expect(store.getters['currentTimeFormatted'](state)).to.equal('00:13')
    })
    it('progress', () => {
      const state = { currentTime: 4, duration: 10 }
      expect(store.getters['progress'](state)).to.equal(40)
    })
  })
  describe('actions', () => {
    it('incrementVolume', (done) => {
      testAction({
        action: store.actions.incrementVolume,
        payload: 0.2,
        params: {state: {volume: 0.7}},
        expectedMutations: [
          { type: 'volume', payload: 0.7 + 0.2 }
        ]
      }, done)
    })
    it('toggle play false', (done) => {
      testAction({
        action: store.actions.togglePlay,
        params: {state: {playing: false}},
        expectedMutations: [
          { type: 'playing', payload: true }
        ]
      }, done)
    })
    it('toggle play true', (done) => {
      testAction({
        action: store.actions.togglePlay,
        params: {state: {playing: true}},
        expectedMutations: [
          { type: 'playing', payload: false }
        ]
      }, done)
    })
    it('trackEnded', (done) => {
      testAction({
        action: store.actions.trackEnded,
        payload: {test: 'track'},
        params: {rootState: {queue: {currentIndex:0, tracks: [1, 2]}}},
        expectedActions: [
          { type: 'trackListened', payload: {test: 'track'} },
          { type: 'queue/next', payload: null, options: {root: true} }
        ]
      }, done)
    })
    it('trackEnded calls populateQueue if last', (done) => {
      testAction({
        action: store.actions.trackEnded,
        payload: {test: 'track'},
        params: {rootState: {queue: {currentIndex:1, tracks: [1, 2]}}},
        expectedActions: [
          { type: 'trackListened', payload: {test: 'track'} },
          { type: 'radios/populateQueue', payload: null, options: {root: true} },
          { type: 'queue/next', payload: null, options: {root: true} }
        ]
      }, done)
    })
    it('trackErrored', (done) => {
      testAction({
        action: store.actions.trackErrored,
        payload: {test: 'track'},
        params: {state: {errorCount: 0, maxConsecutiveErrors: 5}},
        expectedMutations: [
          { type: 'errored', payload: true },
          { type: 'incrementErrorCount' }
        ],
        expectedActions: [
          { type: 'queue/next', payload: null, options: {root: true} }
        ]
      }, done)
    })
    it('updateProgress', (done) => {
      testAction({
        action: store.actions.updateProgress,
        payload: 1,
        expectedMutations: [
          { type: 'currentTime', payload: 1 }
        ]
      }, done)
    })
  })
})
