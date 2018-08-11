import {expect} from 'chai'

import Username from '@/components/common/Username.vue'

import { render } from '../../utils'

describe('Username', () => {
  it('displays username', () => {
    const vm = render(Username, {username: 'Hello'})
    expect(vm.$el.textContent).to.equal('Hello')
  })
})
