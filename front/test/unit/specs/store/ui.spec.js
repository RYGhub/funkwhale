import store from '@/store/ui'

describe('store/ui', () => {
  describe('mutations', () => {
    it('addMessage', () => {
      const state = {maxMessages: 100, messages: []}
      store.mutations.addMessage(state, 'hello')
      expect(state.messages).to.deep.equal(['hello'])
    })
    it('addMessage', () => {
      const state = {maxMessages: 1, messages: ['hello']}
      store.mutations.addMessage(state, 'world')
      expect(state.messages).to.deep.equal(['world'])
    })
  })
})
