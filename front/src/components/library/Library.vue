<template>
  <div class="main library pusher">
    <nav class="ui secondary pointing menu" role="navigation" :aria-label="labels.secondaryMenu">
      <router-link class="ui item" to="/library" exact>
        <translate translate-context="*/Library/*/Verb">Browse</translate>
      </router-link>
      <router-link class="ui item" to="/library/albums" exact>
        <translate translate-context="*/*/*">Albums</translate>
      </router-link>
      <router-link class="ui item" to="/library/artists" exact>
        <translate translate-context="*/*/*/Noun">Artists</translate>
      </router-link>
      <router-link class="ui item" to="/library/radios" exact>
        <translate translate-context="*/*/*">Radios</translate>
      </router-link>
      <router-link class="ui item" to="/library/playlists" exact>
        <translate translate-context="*/*/*">Playlists</translate>
      </router-link>
    </nav>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  computed: {
    showImports() {
      return (
        this.$store.state.auth.availablePermissions["upload"] ||
        this.$store.state.auth.availablePermissions["library"]
      )
    },
    labels() {
      return {
        secondaryMenu: this.$pgettext('Menu/*/Hidden text', "Secondary menu")
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
@import "../../style/vendor/media";

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
        &,
        .sub {
          text-shadow: 0 1px 0 rgba(0, 0, 0, 0.8);
          color: white !important;
        }
      }
      .segment-content {
        background-color: rgba(0, 0, 0, 0.5);
      }
    }
  }
}
</style>
