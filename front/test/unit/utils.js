// helper for testing action with expected mutations
import Vue from 'vue'

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

    try {
      expect(mutation.type).to.equal(type)
      if (payload) {
        expect(mutation.payload).to.deep.equal(payload)
      }
    } catch (error) {
      done(error)
    }

    mutationsCount++
    if (isOver()) {
      done()
    }
  }
  // mock dispatch
  const dispatch = (type, payload, options) => {
    const a = expectedActions[actionsCount]
    try {
      expect(a.type).to.equal(type)
      if (payload) {
        expect(a.payload).to.deep.equal(payload)
      }
      if (a.options) {
        expect(options).to.deep.equal(a.options)
      }
    } catch (error) {
      done(error)
    }

    actionsCount++
    if (isOver()) {
      done()
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
      done()
    }
  }
  // call the action with mocked store and arguments
  let promise = action({ commit, dispatch, ...params }, payload)
  if (promise) {
    return promise.then(end)
  } else {
    return end()
  }
}
