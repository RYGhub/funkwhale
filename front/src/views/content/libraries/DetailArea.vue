<template>
  <div>
    <div class="ui two column row">
      <div class="column">
        <h3 class="ui header"><translate translate-context="Content/Library/Title">Current library</translate></h3>
        <library-card :library="library" />
        <radio-button :type="'library'" :object-id="library.uuid"></radio-button>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <slot></slot>
  </div>
</template>

<script>
import RadioButton from '@/components/radios/Button'
import LibraryCard from './Card'

export default {
  props: ['library'],
  components: {
    LibraryCard,
    RadioButton,
  },
  computed: {
    links () {
      let upload = this.$pgettext('Content/Library/Card.Button.Label/Verb', 'Upload')
      return [
        {
          name: 'libraries.detail.upload',
          label: upload
        }
      ]
    }
  }
}
</script>
