<template>
  <div class="main pusher"  v-title="labels.title">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'manage.library.files'}"><translate>Files</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'manage.library.requests'}">
          <translate>Import requests</translate>
          <div
            :class="['ui', {'teal': $store.state.ui.notifications.importRequests > 0}, 'label']"
            :title="labels.pendingRequests">
            {{ $store.state.ui.notifications.importRequests }}</div>
          </router-link>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels () {
      let title = this.$gettext('Manage library')
      let pendingRequests = this.$gettext('Pending import requests')
      return {
        title,
        pendingRequests
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
