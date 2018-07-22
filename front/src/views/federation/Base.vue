<template>
  <div class="main pusher"  v-title="labels.title">
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
            <div class="ui teal label" :title="labels.pendingRequests">{{ requestsCount }}</div>
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
  computed: {
    labels () {
      let title = this.$gettext('Federation')
      let pendingRequests = this.$gettext('Pending requests')
      return {
        title,
        pendingRequests
      }
    }
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
