<template>
  <div>
    <div class="ui stackable grid">
      <div class="eleven wide stretched column">
        <slot name="header"></slot>
      </div>
      <div class="five wide column">
        <h3 class="ui header"><translate>Current library</translate></h3>
        <library-card :library="library" />
      </div>
    </div>
    <div class="ui divider"></div>
    <slot></slot>
  </div>
</template>

<script>
import LibraryCard from './Card'

export default {
  props: ['library'],
  components: {
    LibraryCard
  },
  computed: {
    links () {
      let upload = this.$gettext('Upload')
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
