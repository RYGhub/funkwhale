import {expect} from 'chai'

import {parseAPIErrors} from '@/utils'

describe('utils', () => {
  describe('parseAPIErrors', () => {
    it('handles flat structure', () => {
      const input = {"old_password": ["Invalid password"]}
      let expected = ["Invalid password"]
      let output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('handles flat structure with multiple errors per field', () => {
      const input = {"old_password": ["Invalid password", "Too short"]}
      let expected = ["Invalid password", "Too short"]
      let output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('translate field name', () => {
      const input = {"old_password": ["This field is required"]}
      let expected = ["Old Password: This field is required"]
      let output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('handle nested fields', () => {
      const input = {"summary": {"text": ["Ensure this field has no more than 5000 characters."]}}
      let expected = ["Summary - Text: Ensure this field has no more than 5000 characters."]
      let output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
  })
})
