<template>
  <div class="ui fluid action input">
    <p class="message" v-if="copied">
      <translate>Text copied to clipboard!</translate>
    </p>
    <input ref="input" :value="value" type="text">
    <button @click="copy" class="ui teal right labeled icon button">
      <i class="copy icon"></i>
      <translate>Copy</translate>
    </button>
  </div>
</template>
<script>
export default {
  props: ['value'],
  data () {
    return {
      copied: false,
      timeout: null
    }
  },
  methods: {
    copy () {
      if (this.timeout) {
        clearTimeout(this.timeout)
      }
      this.$refs.input.select()
      document.execCommand("Copy")
      let self = this
      self.copied = true
      this.timeout = setTimeout(() => {
        self.copied = false
      }, 5000)
    }
  }
}
</script>
<style scoped>
.message {
  position: absolute;
  right: 0;
  bottom: -3em;
}
</style>
