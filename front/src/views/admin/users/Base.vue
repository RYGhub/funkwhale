<template>
  <div class="main pusher"  v-title="$gettext('Manage users')">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'manage.users.users.list'}"><translate>Users</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'manage.users.invitations.list'}"><translate>Invitations</translate></router-link>
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
