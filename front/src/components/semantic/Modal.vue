<template>
  <div :class="['ui', {'active': show}, 'modal']">
    <i class="close icon"></i>
    <slot>
      
    </slot>
  </div>
</template>

<script>
import $ from 'jquery'

export default {
  props: {
    show: {type: Boolean, required: true}
  },
  data () {
    return {
      control: null
    }
  },
  mounted () {
    this.control = $(this.$el).modal({
      onApprove: function () {
        this.$emit('approved')
      }.bind(this),
      onDeny: function () {
        this.$emit('deny')
      }.bind(this),
      onHidden: function () {
        this.$emit('update:show', false)
      }.bind(this)
    })
  },
  watch: {
    show: {
      handler (newValue) {
        if (newValue) {
          this.control.modal('show')
        } else {
          this.control.modal('hide')
        }
      }
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
