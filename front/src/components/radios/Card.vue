<template>
    <div class="ui card">
      <div class="content">
        <div class="header">
          <router-link v-if="radio.id" class="discrete link" :to="{name: 'library.radios.detail', params: {id: radio.id}}">
            {{ radio.name }}
          </router-link>
          <template v-else>
            {{ radio.name }}
          </template>
        </div>
        <div class="description">
          {{ radio.description }}
        </div>
      </div>
      <div class="extra content">
        <user-link :user="radio.user" class="left floated" />
        <radio-button class="right floated button" :type="type" :custom-radio-id="customRadioId"></radio-button>
        <router-link
          class="ui basic yellow button right floated"
          v-if="$store.state.auth.authenticated && type === 'custom' && radio.user.id === $store.state.auth.profile.id"
          :to="{name: 'library.radios.edit', params: {id: customRadioId }}">
          <translate>Edit...</translate>
        </router-link>
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
