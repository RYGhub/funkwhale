<template>
  <button @click="toggleRadio" :class="['ui', 'blue', {'inverted': running}, 'button']">
    <i class="ui feed icon"></i>
    <template v-if="running">Stop</template>
    <template v-else>Start</template>
    radio
  </button>
</template>

<script>

import radios from '@/radios'

export default {
  props: {
    type: {type: String, required: true},
    objectId: {type: Number, default: null}
  },
  data () {
    return {
      radios
    }
  },
  methods: {
    toggleRadio () {
      if (this.running) {
        radios.stop()
      } else {
        radios.start(this.type, this.objectId)
      }
    }
  },
  computed: {
    running () {
      if (!radios.running) {
        return false
      } else {
        return radios.current.type === this.type & radios.current.objectId === this.objectId
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
