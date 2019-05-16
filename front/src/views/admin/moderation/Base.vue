<template>
  <div class="main pusher"  v-title="labels.moderation">
    <nav class="ui secondary pointing menu" role="navigation" :aria-label="labels.secondaryMenu">
      <router-link
        class="ui item"
        :to="{name: 'manage.moderation.domains.list'}"><translate translate-context="*/Moderation/*/Noun">Domains</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'manage.moderation.accounts.list'}"><translate translate-context="*/Moderation/Title">Accounts</translate></router-link>

    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels() {
      return {
        moderation: this.$pgettext('*/Moderation/*', "Moderation"),
        secondaryMenu: this.$pgettext('Menu/*/Hidden text', "Secondary menu")
      }
    }
  }
}
</script>
