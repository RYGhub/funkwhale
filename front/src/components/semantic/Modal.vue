<template>
  <div :class="['ui', {'active': show}, 'modal']">
    <i class="close icon"></i>
    <slot v-if="show">

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
  beforeDestroy () {
    if (this.control) {
      $(this.$el).modal('hide')
    }
    $(this.$el).remove()
  },
  methods: {
    initModal () {
      this.control = $(this.$el).modal({
        duration: 100,
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
    }
  },
  watch: {
    show: {
      handler (newValue) {
        if (newValue) {
          this.initModal()
          this.$emit('show')
          this.control.modal('show')
        } else {
          if (this.control) {
            this.$emit('hide')
            this.control.modal('hide')
            this.control.remove()
          }
        }
      }
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
