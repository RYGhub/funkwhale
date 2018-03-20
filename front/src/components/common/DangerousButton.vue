<template>
  <div @click="showModal = true" class="ui red button">
    <slot></slot>

    <modal class="small" :show.sync="showModal">
      <div class="header">
        <slot name="modal-header">Do you want to confirm this action?</slot>
      </div>
      <div class="scrolling content">
        <div class="description">
          <slot name="modal-content"></slot>
        </div>
      </div>
      <div class="actions">
        <div class="ui cancel button">Cancel</div>
        <div class="ui confirm red button" @click="confirm">
          <slot name="modal-confirm">Confirm</slot>
        </div>
      </div>
    </modal>
  </div>

</template>
<script>
import Modal from '@/components/semantic/Modal'

export default {
  props: ['action'],
  components: {
    Modal
  },
  data () {
    return {
      showModal: false
    }
  },
  methods: {
    confirm () {
      this.showModal = false
      this.action()
    }
  }
}
</script>
