<template>
  <button @click="toggleRadio" :class="['ui', 'blue', {'inverted': running}, 'icon', 'labeled', 'button']">
    <i class="ui feed icon"></i>
    <template v-if="running"><translate translate-context="*/Player/Button.Label/Short, Verb">Stop radio</translate></template>
    <template v-else><translate translate-context="*/Queue/Button.Label/Short, Verb">Start radio</translate></template>
  </button>
</template>

<script>

export default {
  props: {
    customRadioId: {required: false},
    type: {type: String, required: false},
    objectId: {default: null}
  },
  methods: {
    toggleRadio () {
      if (this.running) {
        this.$store.dispatch('radios/stop')
      } else {
        this.$store.dispatch('radios/start', {type: this.type, objectId: this.objectId, customRadioId: this.customRadioId})
      }
    }
  },
  computed: {
    running () {
      let state = this.$store.state.radios
      let current = state.current
      if (!state.running) {
        return false
      } else {
        return current.type === this.type && current.objectId === this.objectId && current.customRadioId === this.customRadioId
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
i {
  cursor: pointer;
}
</style>
