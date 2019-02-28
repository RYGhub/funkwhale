<template>
  <div class="ui small placeholder segment">
    <div class="ui header">
      <div class="content">
        <slot name="title">

          <i class="search icon"></i>
          <translate :translate-context="'Content/*/Paragraph'">
            No results were found.
          </translate>
        </slot>
      </div>
    </div>
    <div class="inline">
      <slot></slot>
      <button v-if="refresh" class="ui button" @click="$emit('refresh')">
        <translate :translate-context="'Content/Button/Label/Verb'">
          Refresh
        </translate></button>
      </button>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    refresh: {type: Boolean, default: false}
  }
}
</script>

<style>
.ui.small.placeholder.segment {
  min-height: auto;
}
.ui.header .content {
  text-align: center;
  display: block;
}
</style>
