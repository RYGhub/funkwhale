var sinon = require('sinon')
import {expect} from 'chai'

import moxios from 'moxios'
import store from '@/store/radios'
import { testAction } from '../../utils'

describe('store/radios', () => {
  var sandbox

  beforeEach(function () {
    sandbox = sinon.createSandbox()
    moxios.install()
  })
  afterEach(function () {
    sandbox.restore()
    moxios.uninstall()
  })

  describe('mutations', () => {
    it('current', () => {
      const state = {}
      store.mutations.current(state, 1)
      expect(state.current).to.equal(1)
    })
    it('running', () => {
      const state = {}
      store.mutations.running(state, false)
      expect(state.running).to.equal(false)
    })
  })
  describe('actions', () => {
    it('start', () => {
      moxios.stubRequest('radios/sessions/', {
        status: 200,
        response: {id: 2}
      })
      testAction({
        action: store.actions.start,
        payload: {type: 'favorites', objectId: 0, customRadioId: null},
        expectedMutations: [
          {
            type: 'current',
            payload: {
              type: 'favorites',
              objectId: 0,
              customRadioId: null,
              session: 2
            }
          },
          { type: 'running', payload: true }
        ],
        expectedActions: [
          { type: 'populateQueue' }
        ]
      })
    })
    it('stop', () => {
      return testAction({
        action: store.actions.stop,
        params: {state: {}},
        expectedMutations: [
          { type: 'current', payload: null },
          { type: 'running', payload: false }
        ]
      })
    })
    it('populateQueue', () => {
      moxios.stubRequest('radios/tracks/', {
        status: 201,
        response: {track: {id: 1}}
      })
      return testAction({
        action: store.actions.populateQueue,
        params: {
          state: {running: true, current: {session: 1}},
          rootState: {player: {errorCount: 0, maxConsecutiveErrors: 5}}

        },
        expectedActions: [
          { type: 'queue/append', payload: {track: {id: 1}}, options: {root: true} }
        ]
      })
    })
    it('populateQueue does nothing when not running', () => {
      testAction({
        action: store.actions.populateQueue,
        params: {state: {running: false}},
        expectedActions: []
      })
    })
    it('populateQueue does nothing when too much errors', () => {
      return testAction({
        action: store.actions.populateQueue,
        payload: {test: 'track'},
        params: {
          rootState: {player: {errorCount: 5, maxConsecutiveErrors: 5}},
          state: {running: true}
        },
        expectedActions: []
      })
    })
  })
})
