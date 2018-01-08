import store from '@/store/player'

describe('mutations', () => {
  it('set volume', () => {
    // mock state
    const state = { volume: 0 }
    // apply mutation
    store.mutations.volume(state, 0.9)
    // assert result
    expect(state.volume).to.equal(0.9)
  })
  it('set volume max 1', () => {
    // mock state
    const state = { volume: 0 }
    // apply mutation
    store.mutations.volume(state, 2)
    // assert result
    expect(state.volume).to.equal(1)
  })
  it('set volume min to 0', () => {
    // mock state
    const state = { volume: 0.5 }
    // apply mutation
    store.mutations.volume(state, -2)
    // assert result
    expect(state.volume).to.equal(0)
  })
  it('increment volume', () => {
    // mock state
    const state = { volume: 0 }
    // apply mutation
    store.mutations.incrementVolume(state, 0.1)
    // assert result
    expect(state.volume).to.equal(0.1)
  })
  it('increment volume max 1', () => {
    // mock state
    const state = { volume: 0 }
    // apply mutation
    store.mutations.incrementVolume(state, 2)
    // assert result
    expect(state.volume).to.equal(1)
  })
  it('increment volume min to 0', () => {
    // mock state
    const state = { volume: 0.5 }
    // apply mutation
    store.mutations.incrementVolume(state, -2)
    // assert result
    expect(state.volume).to.equal(0)
  })
})
