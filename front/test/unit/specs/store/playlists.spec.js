var sinon = require('sinon')
import moxios from 'moxios'
import store from '@/store/playlists'

import { testAction } from '../../utils'

describe('store/playlists', () => {
  var sandbox

  beforeEach(function () {
    sandbox = sinon.sandbox.create()
    moxios.install()
  })
  afterEach(function () {
    sandbox.restore()
    moxios.uninstall()
  })

  describe('mutations', () => {
    it('set playlists', () => {
      const state = { playlists: [] }
      store.mutations.playlists(state, [{id: 1, name: 'test'}])
      expect(state.playlists).to.deep.equal([{id: 1, name: 'test'}])
    })
  })
  describe('actions', () => {
    it('fetchOwn does nothing with no user', (done) => {
      testAction({
        action: store.actions.fetchOwn,
        payload: null,
        params: {state: { playlists: [] }, rootState: {auth: {profile: {}}}},
        expectedMutations: []
      }, done)
    })
  })
})
