<template>
  <div class="main pusher"  v-title="labels.manageUsers">
    <nav class="ui secondary pointing menu" role="navigation" :aria-label="labels.secondaryMenu">
      <router-link
        class="ui item"
        :to="{name: 'manage.users.users.list'}"><translate translate-context="*/Admin/Link">Users</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'manage.users.invitations.list'}"><translate translate-context="Menu/Admin/Link">Invitations</translate></router-link>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels() {
      return {
        manageUsers: this.$pgettext('Head/Admin/Title', 'Manage users'),
        secondaryMenu: this.$pgettext('Menu/*/Hidden text','Secondary menu')
      }
    }
  }
}
</script>
