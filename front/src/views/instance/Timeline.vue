<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical center aligned stripe segment">
      <div v-if="isLoading" :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
        <div class="ui text loader"><translate>Loading timeline...</translate></div>
      </div>
      <div v-else class="ui text container">
        <h1 class="ui header"><translate>Recent activity on this instance</translate></h1>
        <div class="ui feed">
          <component
            class="event"
            v-for="(event, index) in events"
            :key="event.id + index"
            v-if="components[event.type]"
            :is="components[event.type]"
            :event="event">
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
      bridge: null,
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
  destroyed () {
    this.disconnect()
  },
  computed: {
    ...mapState({
      events: state => state.instance.events
    }),
    labels () {
      return {
        title: this.$gettext('Instance Timeline')
      }
    }
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
    disconnect () {
      if (!this.bridge) {
        return
      }
      this.bridge.socket.close(1000, 'goodbye', {keepClosed: true})
    },
    openWebsocket () {
      if (!this.$store.state.auth.authenticated) {
        return
      }
      this.disconnect()
      let self = this
      let token = this.$store.state.auth.token
      // let token = 'test'
      const bridge = new WebSocketBridge()
      this.bridge = bridge
      let url = this.$store.getters['instance/absoluteUrl'](`api/v1/instance/activity?token=${token}`)
      url = url.replace('http://', 'ws://')
      url = url.replace('https://', 'wss://')
      bridge.connect(
        url,
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
