<template>
  <a role="button" class="collapse link" @click.prevent="$emit('input', !value)">
    <translate v-if="isCollapsed" key="1" translate-context="*/*/Button,Label">Expand</translate>
    <translate v-else key="2" translate-context="*/*/Button,Label">Collapse</translate>
    <i :class="[{down: !isCollapsed}, {right: isCollapsed}, 'angle', 'icon']"></i>
  </a>
</template>
<script>

export default {
  props: {
    value: {type: Boolean, required: true},
  },
  computed: {
    isCollapsed () {
      return this.value
    }
  }
}
</script>
