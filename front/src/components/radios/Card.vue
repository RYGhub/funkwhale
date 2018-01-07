<template>
    <div class="ui card">
      <div class="content">
        <div class="header">{{ radio.name }}</div>
        <div class="description">
          {{ radio.description }}
        </div>
      </div>
      <div class="extra content">
        <router-link
          class="ui basic yellow button"
          v-if="$store.state.auth.authenticated && type === 'custom' && customRadio.user === $store.state.auth.profile.id"
          :to="{name: 'library.radios.edit', params: {id: customRadioId }}">
          Edit...
        </router-link>
        <radio-button class="right floated button" :type="type" :custom-radio-id="customRadioId"></radio-button>
      </div>
    </div>
</template>

<script>
import RadioButton from './Button'

export default {
  props: {
    type: {type: String, required: true},
    customRadio: {required: false}
  },
  components: {
    RadioButton
  },
  computed: {
    radio () {
      if (this.customRadio) {
        return this.customRadio
      }
      return this.$store.getters['radios/types'][this.type]
    },
    customRadioId: function () {
      if (this.customRadio) {
        return this.customRadio.id
      }
      return null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
