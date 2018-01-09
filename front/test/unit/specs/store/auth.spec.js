import store from '@/store/auth'

import { testAction } from '../../utils'

describe('store/auth', () => {
  describe('mutations', () => {
    it('profile', () => {
      const state = {}
      store.mutations.profile(state, {})
      expect(state.profile).to.deep.equal({})
    })
    it('username', () => {
      const state = {}
      store.mutations.username(state, 'world')
      expect(state.username).to.equal('world')
    })
    it('authenticated true', () => {
      const state = {}
      store.mutations.authenticated(state, true)
      expect(state.authenticated).to.equal(true)
    })
    it('authenticated false', () => {
      const state = {
        username: 'dummy',
        token: 'dummy',
        tokenData: 'dummy',
        profile: 'dummy',
        availablePermissions: 'dummy'
      }
      store.mutations.authenticated(state, false)
      expect(state.authenticated).to.equal(false)
      expect(state.username).to.equal(null)
      expect(state.token).to.equal(null)
      expect(state.tokenData).to.equal(null)
      expect(state.profile).to.equal(null)
      expect(state.availablePermissions).to.deep.equal({})
    })
    it('token null', () => {
      const state = {}
      store.mutations.token(state, null)
      expect(state.token).to.equal(null)
      expect(state.tokenData).to.deep.equal({})
    })
    it('token real', () => {
      // generated on http://kjur.github.io/jsjws/tool_jwt.html
      const state = {}
      let token = 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwczovL2p3dC1pZHAuZXhhbXBsZS5jb20iLCJzdWIiOiJtYWlsdG86bWlrZUBleGFtcGxlLmNvbSIsIm5iZiI6MTUxNTUzMzQyOSwiZXhwIjoxNTE1NTM3MDI5LCJpYXQiOjE1MTU1MzM0MjksImp0aSI6ImlkMTIzNDU2IiwidHlwIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9yZWdpc3RlciJ9.'
      let tokenData = {
        iss: 'https://jwt-idp.example.com',
        sub: 'mailto:mike@example.com',
        nbf: 1515533429,
        exp: 1515537029,
        iat: 1515533429,
        jti: 'id123456',
        typ: 'https://example.com/register'
      }
      store.mutations.token(state, token)
      expect(state.token).to.equal(token)
      expect(state.tokenData).to.deep.equal(tokenData)
    })
    it('permissions', () => {
      const state = { availablePermissions: {} }
      store.mutations.permission(state, {key: 'admin', status: true})
      expect(state.availablePermissions).to.deep.equal({admin: true})
    })
  })
  describe('getters', () => {
    it('header', () => {
      const state = { token: 'helloworld' }
      expect(store.getters['header'](state)).to.equal('JWT helloworld')
    })
  })
  describe('actions', () => {
    it('logout', (done) => {
      testAction({
        action: store.actions.logout,
        params: {state: {}},
        expectedMutations: [
          { type: 'authenticated', payload: false }
        ]
      }, done)
    })
    it('check jwt null', (done) => {
      testAction({
        action: store.actions.check,
        params: {state: {}},
        expectedMutations: [
          { type: 'authenticated', payload: false }
        ]
      }, done)
    })
    it('check jwt set', (done) => {
      testAction({
        action: store.actions.check,
        params: {state: {token: 'test', username: 'user'}},
        expectedMutations: [
          { type: 'authenticated', payload: true },
          { type: 'username', payload: 'user' },
          { type: 'token', payload: 'test' }
        ],
        expectedActions: [
          { type: 'fetchProfile' },
          { type: 'refreshToken' }
        ]
      }, done)
    })
  })
})
