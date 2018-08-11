import {expect} from 'chai'
var sinon = require('sinon')
import moxios from 'moxios'
import store from '@/store/instance'
import { testAction } from '../../utils'

describe('store/instance', () => {
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
    it('settings', () => {
      const state = {settings: {raven: {front_dsn: {value: 'test'}}}}
      let settings = {raven: {front_enabled: {value: true}}}
      store.mutations.settings(state, settings)
      expect(state.settings).to.deep.equal({
        raven: {front_dsn: {value: 'test'}, front_enabled: {value: true}}
      })
    })
  })
  describe('actions', () => {
    it('fetchSettings', () => {
      moxios.stubRequest('instance/settings/', {
        status: 200,
        response: [
          {
            section: 'raven',
            name: 'front_dsn',
            value: 'test'
          },
          {
            section: 'raven',
            name: 'front_enabled',
            value: false
          }
        ]
      })
      testAction({
        action: store.actions.fetchSettings,
        payload: null,
        expectedMutations: [
          {
            type: 'settings',
            payload: {
              raven: {
                front_dsn: {
                  section: 'raven',
                  name: 'front_dsn',
                  value: 'test'
                },
                front_enabled: {
                  section: 'raven',
                  name: 'front_enabled',
                  value: false
                }
              }
            }
          }
        ]
      })
    })
  })
})
