<template>
  <div class="ui vertical stripe segment" v-title="labels.title">
    <div class="ui small text container">
      <h2 class="ui header">
        <translate>Request some music</translate>
      </h2>
      <request-form v-if="$store.state.auth.authenticated"></request-form>
    </div>
  </div>
</template>

<script>
import RequestForm from '@/components/requests/Form'

export default {
  components: {
    RequestForm
  },
  computed: {
    labels () {
      let title = this.$gettext('Request some music')
      return {
        title
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
