<template>
  <div class="main library pusher">
    <div class="ui secondary pointing menu">
      <router-link class="ui item" to="/library" exact>Browse</router-link>
      <router-link v-if="auth.user.availablePermissions['import.launch']" class="ui item" to="/library/import/launch" exact>Import</router-link>
      <router-link v-if="auth.user.availablePermissions['import.launch']" class="ui item" to="/library/import/batches">Import batches</router-link>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>

import auth from '@/auth'

export default {
  name: 'library',
  data: function () {
    return {
      auth
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
.library.pusher > .ui.secondary.menu {
  margin: 0 2.5rem;
}

.library {
  .ui.segment.head {
    background-size: cover;
    background-position: center;
    padding: 0;
    .segment-content {
      margin: 0 auto;
      padding: 4em;
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
