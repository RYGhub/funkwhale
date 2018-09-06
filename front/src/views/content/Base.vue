<template>
  <div class="main pusher"  v-title="labels.title">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'content.libraries.index'}"><translate>Libraries</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'content.libraries.files'}"><translate>Tracks</translate></router-link>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>
<script>

export default {
  computed: {
    labels () {
      let title = this.$gettext('Add content')
      return {
        title
      }
    }
  }
}
</script>
