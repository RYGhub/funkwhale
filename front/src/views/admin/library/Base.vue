<template>
  <div class="main pusher"  v-title="'Manage library'">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'manage.library.files'}">{{ $gettext('Files') }}</router-link>
      <router-link
        class="ui item"
        :to="{name: 'manage.library.requests'}">
          {{ $gettext('Import requests') }}
          <div
            :class="['ui', {'teal': $store.state.ui.notifications.importRequests > 0}, 'label']"
            :title="$gettext('Pending import requests')">
            {{ $store.state.ui.notifications.importRequests }}</div>
          </router-link>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {}
</script>

<style lang="scss">
@import '../../../style/vendor/media';

.main.pusher > .ui.secondary.menu {
  @include media(">tablet") {
    margin: 0 2.5rem;
  }
  .item {
    padding-top: 1.5em;
    padding-bottom: 1.5em;
  }
}
</style>
