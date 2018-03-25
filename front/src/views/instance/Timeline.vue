<template>
  <div class="main pusher">
    <div class="ui vertical center aligned stripe segment">
      <div v-if="isLoading" :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
        <div class="ui text loader">Loading timeline...</div>
      </div>
      <div v-else class="ui text container">
        <h1 class="ui header">Recent activity on this instance</h1>
        <div class="ui feed">
          <component
            class="event"
            v-for="(event, index) in events"
            :key="event.id + index"
            v-if="components[event.type]"
            :is="components[event.type]"
            :event="event">
            <username
              class="user"
              :username="event.actor.local_id"
              slot="user"></username>
              {{ event.published }}
            <human-date class="date" :date="event.published" slot="date"></human-date>
          </component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import { WebSocketBridge } from 'django-channels'
import axios from 'axios'
import logger from '@/logging'

import Like from '@/components/activity/Like'
import Listen from '@/components/activity/Listen'

export default {
  data () {
    return {
      isLoading: false,
      components: {
        'Like': Like,
        'Listen': Listen
      }
    }
  },
  created () {
    this.openWebsocket()
    this.fetchEvents()
  },
  computed: {
    ...mapState({
      events: state => state.instance.events
    })
  },
  methods: {
    fetchEvents () {
      this.isLoading = true
      let self = this
      axios.get('/activity/').then((response) => {
        self.isLoading = false
        self.$store.commit('instance/events', response.data.results)
      })
    },
    openWebsocket () {
      if (!this.$store.state.auth.authenticated) {
        return
      }
      let self = this
      let token = this.$store.state.auth.token
      // let token = 'test'
      const bridge = new WebSocketBridge()
      bridge.connect(
        `/api/v1/instance/activity?token=${token}`,
        null,
        {reconnectInterval: 5000})
      bridge.listen(function (event) {
        logger.default.info('Received timeline update', event)
        self.$store.commit('instance/event', event)
      })
      bridge.socket.addEventListener('open', function () {
        console.log('Connected to WebSocket')
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
