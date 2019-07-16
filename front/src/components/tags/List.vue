<template>
  <div class="tag-list">
    <router-link
      :to="{name: 'library.tags.detail', params: {id: tag}}"
      :class="['ui', 'circular', 'hashtag', 'label', labelClasses]"
      v-for="tag in toDisplay"
      :title="tag"
      :key="tag">
      #{{ tag|truncate(truncateSize) }}
    </router-link>
    <div role="button" @click.prevent="honorLimit = false" class="ui circular inverted teal label" v-if="showMore && toDisplay.length < tags.length">
      <translate translate-context="Content/*/Button/Label/Verb" :translate-params="{count: tags.length - toDisplay.length}" :translate-n="tags.length - toDisplay.length" translate-plural="Show %{ count } more tags">Show 1 more tag</translate>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    tags: {type: Array, required: true},
    showMore: {type: Boolean, default: true},
    truncateSize: {type: Number, default: 25},
    limit: {type: Number, default: 5},
    labelClasses: {type: String, default: ''},
  },
  data () {
    return {
      honorLimit: true,
    }
  },
  computed: {
    toDisplay () {
      if (!this.honorLimit) {
        return this.tags
      }
      return (this.tags || []).slice(0, this.limit)
    }
  }
}
</script>
<style lang="scss" scoped>
.ui.circular.label {
  padding-left: 1em !important;
  padding-right: 1em !important;
}
.hashtag {
  margin: 0.25em;
}
</style>
