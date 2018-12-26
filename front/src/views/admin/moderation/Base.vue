<template>
  <div class="main pusher"  v-title="labels.manageDomains">
    <nav class="ui secondary pointing menu" role="navigation" :aria-label="labels.secondaryMenu">
      <router-link
        class="ui item"
        :to="{name: 'manage.moderation.domains.list'}"><translate>Domains</translate></router-link>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels() {
      return {
        manageDomains: this.$gettext("Manage domains"),
        secondaryMenu: this.$gettext("Secondary menu")
      }
    }
  }
}
</script>
