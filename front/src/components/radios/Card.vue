<template>
    <div class="ui card">
      <div class="content">
        <div class="header">Radio : {{ radio.name }}</div>
        <div class="description">
          {{ radio.description }}
        </div>
      </div>
      <div class="extra content">
        <radio-button class="right floated button" :type="type"></radio-button>
      </div>
    </div>
</template>

<script>
import RadioButton from './Button'

export default {
  props: {
    type: {type: String, required: true}
  },
  components: {
    RadioButton
  },
  computed: {
    radio () {
      return this.$store.getters['radios/types'][this.type]
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
