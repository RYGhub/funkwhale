<template>
  <div @click="showModal = true" :class="['ui', color, {disabled: disabled}, 'button']" :disabled="disabled">
    <slot></slot>

    <modal class="small" :show.sync="showModal">
      <div class="header">
        <slot name="modal-header">
          {{ $gettext('Do you want to confirm this action?') }}
        </slot>
      </div>
      <div class="scrolling content">
        <div class="description">
          <slot name="modal-content"></slot>
        </div>
      </div>
      <div class="actions">
        <div class="ui cancel button">
          {{ $gettext('Cancel') }}
        </div>
        <div :class="['ui', 'confirm', confirmButtonColor, 'button']" @click="confirm">
          <slot name="modal-confirm">
            {{ $gettext('Confirm') }}
          </slot>
        </div>
      </div>
    </modal>
  </div>

</template>
<script>
import Modal from '@/components/semantic/Modal'

export default {
  props: {
    action: {type: Function, required: false},
    disabled: {type: Boolean, default: false},
    color: {type: String, default: 'red'},
    confirmColor: {type: String, default: null, required: false}
  },
  components: {
    Modal
  },
  data () {
    return {
      showModal: false
    }
  },
  computed: {
    confirmButtonColor () {
      if (this.confirmColor) {
        return this.confirmColor
      }
      return this.color
    }
  },
  methods: {
    confirm () {
      this.showModal = false
      this.$emit('confirm')
      if (this.action) {
        this.action()
      }
    }
  }
}
</script>
