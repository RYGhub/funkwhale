<template>
  <div class="main pusher"  v-title="labels.title">
    <nav class="ui secondary pointing menu" role="navigation" :aria-label="labels.secondaryMenu">
      <router-link
        class="ui item"
        :to="{name: 'manage.library.edits'}"><translate translate-context="*/Admin/*/Noun">Edits</translate></router-link>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    labels() {
      let title = this.$pgettext('Head/Admin/Title', 'Manage library')
      let secondaryMenu = this.$pgettext('Menu/*/Hidden text', 'Secondary menu')
      return {
        title,
        secondaryMenu
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
