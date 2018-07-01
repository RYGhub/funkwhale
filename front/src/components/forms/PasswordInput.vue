<template>
  <div class="ui action input">
    <input
    required
    :tabindex="index"
    :type="passwordInputType"
    @input="$emit('input', $event.target.value)"
    :value="value">
    <span @click="showPassword = !showPassword" :title="labels.title" class="ui icon button">
      <i class="eye icon"></i>
    </span>
  </div>
</template>
<script>
export default {
  props: ['value', 'index'],
  data () {
    return {
      showPassword: false
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Show/hide password')
      }
    },
    passwordInputType () {
      if (this.showPassword) {
        return 'text'
      }
      return 'password'
    }
  }
}
</script>
