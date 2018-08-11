import {expect} from 'chai'

import {truncate, markdown, ago, capitalize, year} from '@/filters'

describe('filters', () => {
  describe('truncate', () => {
    it('leave strings as it if correct size', () => {
      const input = 'Hello world'
      let output = truncate(input, 100)
      expect(output).to.equal(input)
    })
    it('returns shorter string with character', () => {
      const input = 'Hello world'
      let output = truncate(input, 5)
      expect(output).to.equal('Hello…')
    })
    it('custom ellipsis', () => {
      const input = 'Hello world'
      let output = truncate(input, 5, ' pouet')
      expect(output).to.equal('Hello pouet')
    })
  })
  describe('markdown', () => {
    it('renders markdown', () => {
      const input = 'Hello world'
      let output = markdown(input)
      expect(output).to.equal('<p>Hello world</p>')
    })
  })
  describe('ago', () => {
    it('works', () => {
      const input = new Date()
      let output = ago(input)
      expect(output).to.equal('a few seconds ago')
    })
  })
  describe('year', () => {
    it('works', () => {
      const input = '2017-07-13'
      let output = year(input)
      expect(output).to.equal(2017)
    })
  })
  describe('capitalize', () => {
    it('works', () => {
      const input = 'hello world'
      let output = capitalize(input)
      expect(output).to.equal('Hello world')
    })
  })
})
