<template>
  <div class="main pusher"  v-title="'Federation'">
    <div class="ui secondary pointing menu">
      <router-link
        class="ui item"
        :to="{name: 'federation.libraries.list'}"><translate>Libraries</translate></router-link>
      <router-link
        class="ui item"
        :to="{name: 'federation.tracks.list'}"><translate>Tracks</translate></router-link>
        <div class="ui secondary right menu">
          <router-link
            class="ui item"
            :to="{name: 'federation.followers.list'}">
            <translate>Followers</translate>
            <div class="ui teal label" :title="$gettext('Pending requests')">{{ requestsCount }}</div>
          </router-link>
        </div>
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>
<script>
import axios from 'axios'
export default {
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
      let self = this
      axios.get('federation/libraries/followers/', {params: {pending: true}}).then(response => {
        self.requestsCount = response.data.count
      })
    }
  }
}
</script>
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
