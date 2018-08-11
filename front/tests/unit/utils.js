// helper for testing action with expected mutations
import Vue from 'vue'
import {expect} from 'chai'


export const render = (Component, propsData) => {
  const Constructor = Vue.extend(Component)
  return new Constructor({ propsData: propsData }).$mount()
}

export const testAction = ({action, payload, params, expectedMutations, expectedActions}, done) => {
  let mutationsCount = 0
  let actionsCount = 0

  if (!expectedMutations) {
    expectedMutations = []
  }
  if (!expectedActions) {
    expectedActions = []
  }
  const isOver = () => {
    return mutationsCount >= expectedMutations.length && actionsCount >= expectedActions.length
  }
  // mock commit
  const commit = (type, payload) => {
    const mutation = expectedMutations[mutationsCount]

    expect(mutation.type).to.equal(type)
    if (payload) {
      expect(mutation.payload).to.deep.equal(payload)
    }

    mutationsCount++
    if (isOver()) {
      return
    }
  }
  // mock dispatch
  const dispatch = (type, payload, options) => {
    const a = expectedActions[actionsCount]
    if (!a) {
      throw Error(`Unexecpted action ${type}`)
    }
    expect(a.type).to.equal(type)
    if (payload) {
      expect(a.payload).to.deep.equal(payload)
    }
    if (a.options) {
      expect(options).to.deep.equal(a.options)
    }
    actionsCount++
    if (isOver()) {
      return
    }
  }

  let end = function () {
    // check if no mutations should have been dispatched
    if (expectedMutations.length === 0) {
      expect(mutationsCount).to.equal(0)
    }
    if (expectedActions.length === 0) {
      expect(actionsCount).to.equal(0)
    }
    if (isOver()) {
      return
    }
  }
  // call the action with mocked store and arguments
  let promise = action({ commit, dispatch, ...params }, payload)
  if (promise) {
    promise.then(end)
    return promise
  } else {
    return end()
  }
}
