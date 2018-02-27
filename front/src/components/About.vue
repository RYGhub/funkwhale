<template>
  <div class="main pusher">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
            <template v-if="instance.name.value">About {{ instance.name.value }}</template>
            <template v-else="instance.name.value">About this instance</template>
        </h1>
        <stats></stats>
      </div>
    </div>
    <div class="ui vertical stripe segment">
      <p v-if="!instance.short_description.value && !instance.long_description.value">
        Unfortunately, owners of this instance did not yet take the time to complete this page.</p>
      <div
        v-if="instance.short_description.value"
        class="ui middle aligned stackable text container">
        <p>{{ instance.short_description.value }}</p>
      </div>
      <div
        v-if="instance.long_description.value"
        class="ui middle aligned stackable text container"
        v-html="$options.filters.markdown(instance.long_description.value)">
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import Stats from '@/components/instance/Stats'

export default {
  components: {
    Stats
  },
  created () {
    this.$store.dispatch('instance/fetchSettings')
  },
  computed: {
    ...mapState({
      instance: state => state.instance.settings.instance
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
