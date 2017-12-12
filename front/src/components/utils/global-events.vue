<script>
import $ from 'jquery'

const modifiersRE = /^[~!&]*/
const nonEventNameCharsRE = /\W+/
const names = {
  '!': 'capture',
  '~': 'once',
  '&': 'passive'
}

function extractEventOptions (eventDescriptor) {
  const [modifiers] = eventDescriptor.match(modifiersRE)
  return modifiers.split('').reduce((options, modifier) => {
    options[names[modifier]] = true
    return options
  }, {})
}

export default {
  render: h => h(),

  mounted () {
    this._listeners = Object.create(null)
    Object.keys(this.$listeners).forEach(event => {
      const handler = this.$listeners[event]
      let wrapper = function (event) {
        // we check here the event is not triggered from an input
        // to avoid collisions
        if (!$(event.target).is(':input, [contenteditable]')) {
          handler(event)
        }
      }
      document.addEventListener(
        event.replace(nonEventNameCharsRE, ''),
        wrapper,
        extractEventOptions(event)
      )
      this._listeners[event] = handler
    })
  },

  beforeDestroy () {
    for (const event in this._listeners) {
      document.removeEventListener(
        event.replace(nonEventNameCharsRE, ''),
        this._listeners[event]
      )
    }
  }
}
</script>
