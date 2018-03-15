<template>
  <div class="main library pusher">
    <div class="ui secondary pointing menu">
      <router-link class="ui item" to="/library" exact>Browse</router-link>
      <router-link class="ui item" to="/library/artists" exact>Artists</router-link>
      <router-link class="ui item" to="/library/radios" exact>Radios</router-link>
      <div class="ui secondary right menu">
        <router-link v-if="$store.state.auth.authenticated" class="ui item" to="/library/requests/" exact>
          Requests
          <div class="ui teal label">{{ requestsCount }}</div>
        </router-link>
        <router-link v-if="$store.state.auth.availablePermissions['import.launch']" class="ui item" to="/library/import/launch" exact>Import</router-link>
        <router-link v-if="$store.state.auth.availablePermissions['import.launch']" class="ui item" to="/library/import/batches">Import batches
        </router-link>
      </div>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'library',
  data () {
    return {
      requestsCount: 0
    }
  },
  created () {
    this.fetchRequestsCount()
  },
  methods: {
    fetchRequestsCount () {
      if (!this.$store.state.authenticated) {
        return
      }
      let self = this
      axios.get('requests/import-requests/', {params: {status: 'pending'}}).then(response => {
        self.requestsCount = response.data.count
      })
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
