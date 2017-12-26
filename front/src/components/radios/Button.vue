<template>
  <button @click="toggleRadio" :class="['ui', 'blue', {'inverted': running}, 'button']">
    <i class="ui feed icon"></i>
    <template v-if="running">Stop</template>
    <template v-else>Start</template>
    radio
  </button>
</template>

<script>

export default {
  props: {
    type: {type: String, required: true},
    objectId: {type: Number, default: null}
  },
  methods: {
    toggleRadio () {
      if (this.running) {
        this.$store.dispatch('radios/stop')
      } else {
        this.$store.dispatch('radios/start', {type: this.type, objectId: this.objectId})
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
        return current.type === this.type & current.objectId === this.objectId
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
