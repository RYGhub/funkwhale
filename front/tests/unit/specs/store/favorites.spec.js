import {expect} from 'chai'

import store from '@/store/favorites'

import { testAction } from '../../utils'

describe('store/favorites', () => {
  describe('mutations', () => {
    it('track true', () => {
      const state = { tracks: [] }
      store.mutations.track(state, {id: 1, value: true})
      expect(state.tracks).to.deep.equal([1])
      expect(state.count).to.deep.equal(1)
    })
    it('track false', () => {
      const state = { tracks: [1] }
      store.mutations.track(state, {id: 1, value: false})
      expect(state.tracks).to.deep.equal([])
      expect(state.count).to.deep.equal(0)
    })
  })
  describe('getters', () => {
    it('isFavorite true', () => {
      const state = { tracks: [1] }
      expect(store.getters['isFavorite'](state)(1)).to.equal(true)
    })
    it('isFavorite false', () => {
      const state = { tracks: [] }
      expect(store.getters['isFavorite'](state)(1)).to.equal(false)
    })
  })
  describe('actions', () => {
    it('toggle true', () => {
      testAction({
        action: store.actions.toggle,
        payload: 1,
        params: {getters: {isFavorite: () => false}},
        expectedActions: [
          { type: 'set', payload: {id: 1, value: true} }
        ]
      })
    })
    it('toggle true', () => {
      testAction({
        action: store.actions.toggle,
        payload: 1,
        params: {getters: {isFavorite: () => true}},
        expectedActions: [
          { type: 'set', payload: {id: 1, value: false} }
        ]
      })
    })
  })
})
