<template>
  <span  class="tooltip" :data-tooltip="content"><i class="question circle icon"></i></span>
</template>

<script>

export default {
  props: {
    content: {type: String, required: true},
  }
}
</script>
