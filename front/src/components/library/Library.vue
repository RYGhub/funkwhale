<template>
  <div class="main library pusher">
    <div class="ui secondary pointing menu">
      <router-link class="ui item" to="/library" exact>
        <translate>Browse</translate>
      </router-link>
      <router-link class="ui item" to="/library/artists" exact>
        <translate>Artists</translate>
      </router-link>
      <router-link class="ui item" to="/library/radios" exact>
        <translate>Radios</translate>
      </router-link>
      <router-link class="ui item" to="/library/playlists" exact>
        <translate>Playlists</translate>
      </router-link>
      <div class="ui secondary right menu">
        <router-link v-if="showImports" class="ui item" to="/library/import/launch" exact>
          <translate>Import</translate>
        </router-link>
        <router-link v-if="showImports" class="ui item" to="/library/import/batches">
          <translate>Import batches</translate>
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
