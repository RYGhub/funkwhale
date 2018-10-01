<template>
  <div class="main pusher"  v-title="labels.title">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'manage.library.files'}"><translate>Files</translate></router-link>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels () {
      let title = this.$gettext('Manage library')
      return {
        title
      }
    }
  }
}
</script>

<style scoped>

.ui.menu .item > .label {
  position: absolute;
  right: -2em;
}

</style>
