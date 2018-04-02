var sinon = require('sinon')
import _ from 'lodash'

import store from '@/store/queue'
import { testAction } from '../../utils'

describe('store/queue', () => {
  var sandbox

  beforeEach(function () {
    // Create a sandbox for the test
    sandbox = sinon.sandbox.create()
  })

  afterEach(function () {
    // Restore all the things made through the sandbox
    sandbox.restore()
  })
  describe('mutations', () => {
    it('currentIndex', () => {
      const state = {}
      store.mutations.currentIndex(state, 2)
      expect(state.currentIndex).to.equal(2)
    })
    it('ended', () => {
      const state = {}
      store.mutations.ended(state, false)
      expect(state.ended).to.equal(false)
    })
    it('tracks', () => {
      const state = {}
      store.mutations.tracks(state, [1, 2])
      expect(state.tracks).to.deep.equal([1, 2])
    })
    it('splice', () => {
      const state = {tracks: [1, 2, 3]}
      store.mutations.splice(state, {start: 1, size: 2})
      expect(state.tracks).to.deep.equal([1])
    })
    it('insert', () => {
      const state = {tracks: [1, 3]}
      store.mutations.insert(state, {track: 2, index: 1})
      expect(state.tracks).to.deep.equal([1, 2, 3])
    })
    it('reorder before', () => {
      const state = {currentIndex: 3}
      store.mutations.reorder(state, {oldIndex: 2, newIndex: 1})
      expect(state.currentIndex).to.equal(3)
    })
    it('reorder from after to before', () => {
      const state = {currentIndex: 3}
      store.mutations.reorder(state, {oldIndex: 4, newIndex: 1})
      expect(state.currentIndex).to.equal(4)
    })
    it('reorder after', () => {
      const state = {currentIndex: 3}
      store.mutations.reorder(state, {oldIndex: 4, newIndex: 5})
      expect(state.currentIndex).to.equal(3)
    })
    it('reorder before to after', () => {
      const state = {currentIndex: 3}
      store.mutations.reorder(state, {oldIndex: 1, newIndex: 5})
      expect(state.currentIndex).to.equal(2)
    })
    it('reorder current', () => {
      const state = {currentIndex: 3}
      store.mutations.reorder(state, {oldIndex: 3, newIndex: 1})
      expect(state.currentIndex).to.equal(1)
    })
  })
  describe('getters', () => {
    it('currentTrack', () => {
      const state = { tracks: [1, 2, 3], currentIndex: 2 }
      expect(store.getters['currentTrack'](state)).to.equal(3)
    })
    it('hasNext true', () => {
      const state = { tracks: [1, 2, 3], currentIndex: 1 }
      expect(store.getters['hasNext'](state)).to.equal(true)
    })
    it('hasNext false', () => {
      const state = { tracks: [1, 2, 3], currentIndex: 2 }
      expect(store.getters['hasNext'](state)).to.equal(false)
    })
  })
  describe('actions', () => {
    it('append at end', (done) => {
      testAction({
        action: store.actions.append,
        payload: {track: 4, skipPlay: true},
        params: {state: {tracks: [1, 2, 3]}},
        expectedMutations: [
          { type: 'insert', payload: {track: 4, index: 3} }
        ]
      }, done)
    })
    it('append at index', (done) => {
      testAction({
        action: store.actions.append,
        payload: {track: 2, index: 1, skipPlay: true},
        params: {state: {tracks: [1, 3]}},
        expectedMutations: [
          { type: 'insert', payload: {track: 2, index: 1} }
        ]
      }, done)
    })
    it('append and play', (done) => {
      testAction({
        action: store.actions.append,
        payload: {track: 3},
        params: {state: {tracks: [1, 2]}},
        expectedMutations: [
          { type: 'insert', payload: {track: 3, index: 2} }
        ],
        expectedActions: [
          { type: 'resume' }
        ]
      }, done)
    })
    it('appendMany', (done) => {
      const tracks = [{title: 1}, {title: 2}]
      testAction({
        action: store.actions.appendMany,
        payload: {tracks: tracks},
        params: {state: {tracks: []}},
        expectedActions: [
          { type: 'append', payload: {track: tracks[0], index: 0, skipPlay: true} },
          { type: 'append', payload: {track: tracks[1], index: 1, skipPlay: true} },
          { type: 'resume' }
        ]
      }, done)
    })
    it('appendMany at index', (done) => {
      const tracks = [{title: 1}, {title: 2}]
      testAction({
        action: store.actions.appendMany,
        payload: {tracks: tracks, index: 1},
        params: {state: {tracks: [1, 2]}},
        expectedActions: [
          { type: 'append', payload: {track: tracks[0], index: 1, skipPlay: true} },
          { type: 'append', payload: {track: tracks[1], index: 2, skipPlay: true} },
          { type: 'resume' }
        ]
      }, done)
    })
    it('cleanTrack after current', (done) => {
      testAction({
        action: store.actions.cleanTrack,
        payload: 3,
        params: {state: {currentIndex: 2}},
        expectedMutations: [
          { type: 'splice', payload: {start: 3, size: 1} }
        ]
      }, done)
    })
    it('cleanTrack before current', (done) => {
      testAction({
        action: store.actions.cleanTrack,
        payload: 1,
        params: {state: {currentIndex: 2}},
        expectedMutations: [
          { type: 'splice', payload: {start: 1, size: 1} }
        ],
        expectedActions: [
          { type: 'currentIndex', payload: 1 }
        ]
      }, done)
    })
    it('cleanTrack current', (done) => {
      testAction({
        action: store.actions.cleanTrack,
        payload: 2,
        params: {state: {currentIndex: 2}},
        expectedMutations: [
          { type: 'splice', payload: {start: 2, size: 1} }
        ],
        expectedActions: [
          { type: 'player/stop', payload: null, options: {root: true} },
          { type: 'currentIndex', payload: 2 }
        ]
      }, done)
    })
    it('resume when ended', (done) => {
      testAction({
        action: store.actions.resume,
        params: {state: {ended: true}, rootState: {player: {errored: false}}},
        expectedActions: [
          { type: 'next' }
        ]
      }, done)
    })
    it('resume when errored', (done) => {
      testAction({
        action: store.actions.resume,
        params: {state: {ended: false}, rootState: {player: {errored: true}}},
        expectedActions: [
          { type: 'next' }
        ]
      }, done)
    })
    it('skip resume when not ended or not error', (done) => {
      testAction({
        action: store.actions.resume,
        params: {state: {ended: false}, rootState: {player: {errored: false}}},
        expectedActions: []
      }, done)
    })
    it('previous when at beginning', (done) => {
      testAction({
        action: store.actions.previous,
        params: {state: {currentIndex: 0}},
        expectedActions: [
          { type: 'currentIndex', payload: 0 }
        ]
      }, done)
    })
    it('previous after less than 3 seconds of playback', (done) => {
      testAction({
        action: store.actions.previous,
        params: {state: {currentIndex: 1}, rootState: {player: {currentTime: 1}}},
        expectedActions: [
          { type: 'currentIndex', payload: 0 }
        ]
      }, done)
    })
    it('previous after more than 3 seconds of playback', (done) => {
      testAction({
        action: store.actions.previous,
        params: {state: {currentIndex: 1}, rootState: {player: {currentTime: 3}}},
        expectedActions: [
          { type: 'currentIndex', payload: 1 }
        ]
      }, done)
    })
    it('next on last track when looping on queue', (done) => {
      testAction({
        action: store.actions.next,
        params: {state: {tracks: [1, 2], currentIndex: 1}, rootState: {player: {looping: 2}}},
        expectedActions: [
          { type: 'currentIndex', payload: 0 }
        ]
      }, done)
    })
    it('next track when last track', (done) => {
      testAction({
        action: store.actions.next,
        params: {state: {tracks: [1, 2], currentIndex: 1}, rootState: {player: {looping: 0}}},
        expectedMutations: [
          { type: 'ended', payload: true }
        ]
      }, done)
    })
    it('next track when not last track', (done) => {
      testAction({
        action: store.actions.next,
        params: {state: {tracks: [1, 2], currentIndex: 0}, rootState: {player: {looping: 0}}},
        expectedActions: [
          { type: 'currentIndex', payload: 1 }
        ]
      }, done)
    })
    it('currentIndex', (done) => {
      testAction({
        action: store.actions.currentIndex,
        payload: 1,
        params: {state: {tracks: [1, 2], currentIndex: 0}, rootState: {radios: {running: false}}},
        expectedMutations: [
          { type: 'ended', payload: false },
          { type: 'player/currentTime', payload: 0, options: {root: true} },
          { type: 'player/playing', payload: true, options: {root: true} },
          { type: 'player/errored', payload: false, options: {root: true} },
          { type: 'currentIndex', payload: 1 }
        ]
      }, done)
    })
    it('currentIndex with radio and many tracks remaining', (done) => {
      testAction({
        action: store.actions.currentIndex,
        payload: 1,
        params: {state: {tracks: [1, 2, 3, 4], currentIndex: 0}, rootState: {radios: {running: true}}},
        expectedMutations: [
          { type: 'ended', payload: false },
          { type: 'player/currentTime', payload: 0, options: {root: true} },
          { type: 'player/playing', payload: true, options: {root: true} },
          { type: 'player/errored', payload: false, options: {root: true} },
          { type: 'currentIndex', payload: 1 }
        ]
      }, done)
    })
    it('currentIndex with radio and less than two tracks remaining', (done) => {
      testAction({
        action: store.actions.currentIndex,
        payload: 1,
        params: {state: {tracks: [1, 2, 3], currentIndex: 0}, rootState: {radios: {running: true}}},
        expectedMutations: [
          { type: 'ended', payload: false },
          { type: 'player/currentTime', payload: 0, options: {root: true} },
          { type: 'player/playing', payload: true, options: {root: true} },
          { type: 'player/errored', payload: false, options: {root: true} },
          { type: 'currentIndex', payload: 1 }
        ],
        expectedActions: [
          { type: 'radios/populateQueue', payload: null, options: {root: true} }
        ]
      }, done)
    })
    it('clean', (done) => {
      testAction({
        action: store.actions.clean,
        expectedMutations: [
          { type: 'tracks', payload: [] },
          { type: 'ended', payload: true }
        ],
        expectedActions: [
          { type: 'radios/stop', payload: null, options: {root: true} },
          { type: 'player/stop', payload: null, options: {root: true} },
          { type: 'currentIndex', payload: -1 }
        ]
      }, done)
    })
    it('shuffle', (done) => {
      let _shuffle = sandbox.stub(_, 'shuffle')
      let tracks = ['a', 'b', 'c', 'd', 'e']
      let shuffledTracks = ['e', 'd', 'c']
      _shuffle.returns(shuffledTracks)
      testAction({
        action: store.actions.shuffle,
        params: {state: {currentIndex: 1, tracks: tracks}},
        expectedMutations: [
          { type: 'player/currentTime', payload: 0 , options: {root: true}},
          { type: 'tracks', payload: [] }
        ],
        expectedActions: [
          { type: 'appendMany', payload: {tracks: ['a', 'b'].concat(shuffledTracks)} }
        ]
      }, done)
    })
  })
})
