<template>
  <div class="main pusher"  v-title="'Federation'">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'federation.libraries.list'}">Libraries</router-link>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>
<style lang="scss">
@import '../../style/vendor/media';

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
