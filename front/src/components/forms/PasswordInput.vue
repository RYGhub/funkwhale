<template>
  <div class="ui action input">
    <input
    required
    :tabindex="index"
    :type="passwordInputType"
    @input="$emit('input', $event.target.value)"
    :value="value">
    <span @click="showPassword = !showPassword" :title="$gettext('Show/hide password')" class="ui icon button">
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
    passwordInputType () {
      if (this.showPassword) {
        return 'text'
      }
      return 'password'
    }
  }
}
</script>
