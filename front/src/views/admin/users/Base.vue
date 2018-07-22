<template>
  <div class="main pusher"  v-title="labels.manageUsers">
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
export default {
  computed: {
    labels () {
      return {
        manageUsers: this.$gettext('Manage users')
      }
    }
  }
}
</script>
