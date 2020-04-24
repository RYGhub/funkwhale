<template>
  <div class="expandable-wrapper">
    <div :class="['expandable-content', {expandable: truncated.length < content.length}, {expanded: isExpanded}]">
      <slot>{{ content }}</slot>
    </div>
    <a v-if="truncated.length < content.length" role="button" @click.prevent="isExpanded = !isExpanded">
      <br>
      <translate v-if="isExpanded" key="1" translate-context="*/*/Button,Label">Show less</translate>
      <translate v-else key="2" translate-context="*/*/Button,Label">Show more</translate>
    </a>
  </div>
</template>
<script>
// import sanitize from "@/sanitize"

export default {
  props: {
    content: {type: String, required: true},
    length: {type: Number, default: 150, required: false},
  },
  data () {
    return {
      isExpanded: false,
    }
  },
  computed: {
    truncated () {
      return this.content.substring(0, this.length)
    }
  }
}
</script>
