<template>
  <form class="ui inline form" @submit.stop.prevent="$emit('search', value)">
    <div :class="['ui', 'action', {icon: isClearable}, 'input']">
      <label for="search-query" class="hidden">
        <translate translate-context="Content/Search/Input.Label/Noun">Search</translate>
      </label>
      <input id="search-query" name="search-query" type="text" :placeholder="placeholder || labels.searchPlaceholder" :value="value" @input="$emit('input', $event.target.value)">
      <i v-if="isClearable" class="x link icon" :title="labels.clear" @click.stop.prevent="$emit('input', ''); $emit('search', value)"></i>
      <button type="submit" class="ui icon basic button">
        <i class="search icon"></i>
      </button>
    </div>
  </form>
</template>
<script>
export default {
  props: {
    value: {type: String, required: true},
    placeholder: {type: String, required: false},
  },
  computed: {
    labels () {
      return {
        searchPlaceholder: this.$pgettext('Content/Search/Input.Placeholder', 'Search…'),
        clear: this.$pgettext("Content/Library/Button.Label", 'Clear'),
      }
    },
    isClearable () {
      return !!this.value
    }
  }
}
</script>
