<template>
  <div class="ui message">
    <div class="content">
      <slot></slot>
    </div>
    <i class="close icon"></i>
  </div>
</template>
<script>
import $ from 'jquery'

export default {
  mounted () {
    let self = this
    $(this.$el).on('click', function () {
      $(self.$el).transition('fade', 125)
    })
  }
}
</script>
<style scoped>
.ui.message .content {
  padding-right: 0.5em;
  cursor: pointer;
}
.ui.message .content :first-child {
  margin-top: 0;
}

.ui.message .content :last-child {
  margin-bottom: 0;
}
</style>
