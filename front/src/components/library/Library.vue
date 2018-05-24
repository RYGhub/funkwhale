<template>
  <div class="main library pusher">
    <div class="ui secondary pointing menu">
      <router-link class="ui item" to="/library" exact><i18next path="Browse"/></router-link>
      <router-link class="ui item" to="/library/artists" exact><i18next path="Artists"/></router-link>
      <router-link class="ui item" to="/library/radios" exact><i18next path="Radios"/></router-link>
      <router-link class="ui item" to="/library/playlists" exact><i18next path="Playlists"/></router-link>
      <div class="ui secondary right menu">
        <router-link
          v-if="$store.state.auth.authenticated"
          class="ui item"
          :to="{name: 'library.requests', query: {status: 'pending' }}"
          exact>
          <i18next path="Requests"/>
        </router-link>
        <router-link v-if="showImports" class="ui item" to="/library/import/launch" exact>
          <i18next path="Import"/>
        </router-link>
        <router-link v-if="showImports" class="ui item" to="/library/import/batches">
          <i18next path="Import batches"/>
        </router-link>
      </div>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    showImports () {
      return this.$store.state.auth.availablePermissions['upload'] || this.$store.state.auth.availablePermissions['library']
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
@import '../../style/vendor/media';

.library.pusher > .ui.secondary.menu {
  @include media(">tablet") {
    margin: 0 2.5rem;
  }
  .item {
    padding-top: 1.5em;
    padding-bottom: 1.5em;
  }
}

.library {
  .ui.segment.head {
    background-size: cover;
    background-position: center;
    padding: 0;
    .segment-content {
      margin: 0 auto;
      padding: 2em;
      @include media(">tablet") {
        padding: 4em;
      }
    }
    &.with-background {
      .header {
        &, .sub, a {
          text-shadow: 0 1px 0 rgba(0, 0, 0, 0.8);
          color: white !important;
        }
      }
      .segment-content {
        background-color: rgba(0, 0, 0, 0.5)
      }

    }
  }

}

</style>
