<template>
  <div id="app">
    <sidebar></sidebar>
    <router-view :key="$route.fullPath"></router-view>
    <div class="ui fitted divider"></div>
    <div id="footer" class="ui vertical footer segment">
      <div class="ui container">
        <div class="ui stackable equal height stackable grid">
          <div class="three wide column">
            <h4 class="ui header">Links</h4>
            <div class="ui link list">
              <router-link class="item" to="/about">
                About this instance
              </router-link>
              <a href="https://funkwhale.audio" class="item" target="_blank">Official website</a>
              <a href="https://docs.funkwhale.audio" class="item" target="_blank">Documentation</a>
              <a href="https://code.eliotberriot.com/funkwhale/funkwhale" class="item" target="_blank">Source code</a>
              <a href="https://code.eliotberriot.com/funkwhale/funkwhale/issues" class="item" target="_blank">Issue tracker</a>
            </div>
          </div>
          <div class="ten wide column">
            <h4 class="ui header">About funkwhale</h4>
            <p>Funkwhale is a free and open-source project run by volunteers. You can help us improve the platform by reporting bugs, suggesting features and share the project with your friends!</p>
          </div>
        </div>
      </div>
    </div>
    <raven
      v-if="$store.state.instance.settings.raven.front_enabled.value"
      :dsn="$store.state.instance.settings.raven.front_dsn.value">
    </raven>
  </div>
</template>

<script>
import { WebSocketBridge } from 'django-channels'

import logger from '@/logging'
import Sidebar from '@/components/Sidebar'
import Raven from '@/components/Raven'

export default {
  name: 'app',
  components: {
    Sidebar,
    Raven
  },
  created () {
    this.$store.dispatch('instance/fetchSettings')
    this.openWebsocket()
    let self = this
    setInterval(() => {
      // used to redraw ago dates every minute
      self.$store.commit('ui/computeLastDate')
    }, 1000 * 60)
  },
  methods: {
    openWebsocket () {
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

<style lang="scss">
// we do the import here instead in main.js
// as resolve order is not deterministric in webpack
// and we end up with CSS rules not applied,
// see https://github.com/webpack/webpack/issues/215
@import 'semantic/semantic.css';
@import 'style/vendor/media';


html, body {
  @include media("<desktop") {
    font-size: 90%;
  }
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.main.pusher, .footer {
  @include media(">desktop") {
    margin-left: 350px !important;
  }
  transform: none !important;
}
.main-pusher {
  padding: 1.5rem 0;
}
.ui.stripe.segment, #footer {
  padding: 2em;
  @include media(">tablet") {
    padding: 4em;
  }
}

.ui.small.text.container {
  max-width: 500px !important;
}

.button.icon.tiny {
    padding: 0.5em !important;
}

.sidebar {
  .logo {
    path {
      fill: white;
    }
  }
}

.discrete.link {
    color: rgba(0, 0, 0, 0.87);
}

.floated.buttons .button ~ .dropdown {
  border-left: none;
}
</style>
