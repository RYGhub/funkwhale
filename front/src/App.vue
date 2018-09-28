<template>
  <div id="app">
    <!-- here, we display custom stylesheets, if any -->
    <link v-for="url in customStylesheets" rel="stylesheet" property="stylesheet" :href="url" :key="url">
    <div class="ui main text container instance-chooser" v-if="!$store.state.instance.instanceUrl">
      <div class="ui padded segment">
        <h1 class="ui header"><translate>Choose your instance</translate></h1>
        <form class="ui form" @submit.prevent="$store.dispatch('instance/setUrl', instanceUrl)">
          <p><translate>You need to select an instance in order to continue</translate></p>
          <div class="ui action input">
            <input type="text" v-model="instanceUrl">
            <button type="submit" class="ui button"><translate>Submit</translate></button>
          </div>
          <p><translate>Suggested choices</translate></p>
          <div class="ui bulleted list">
            <div class="ui item" v-for="url in suggestedInstances">
              <a @click="instanceUrl = url">{{ url }}</a>
            </div>
          </div>
        </form>
      </div>
    </div>
    <template v-else>
      <sidebar></sidebar>
      <service-messages v-if="messages.length > 0" />
      <router-view :key="$route.fullPath"></router-view>
      <div class="ui fitted divider"></div>
      <div id="footer" class="ui vertical footer segment">
        <div class="ui container">
          <div class="ui stackable equal height stackable grid">
            <div class="three wide column">
              <h4 v-translate class="ui header">Links</h4>
              <div class="ui link list">
                <router-link class="item" to="/about">
                  <translate>About this instance</translate>
                </router-link>
                <router-link class="item" :to="{name: 'library.request'}">
                  <translate>Request music</translate>
                </router-link>
                <a href="https://funkwhale.audio" class="item" target="_blank"><translate>Official website</translate></a>
                <a href="https://docs.funkwhale.audio" class="item" target="_blank"><translate>Documentation</translate></a>
                <a href="https://code.eliotberriot.com/funkwhale/funkwhale" class="item" target="_blank">
                  <translate :translate-params="{version: version}" v-if="version">Source code (%{version})</translate>
                  <translate v-else>Source code</translate>
                </a>
                <a href="https://code.eliotberriot.com/funkwhale/funkwhale/issues" class="item" target="_blank"><translate>Issue tracker</translate></a>
                <a @click="switchInstance" class="item" >
                  <translate>Use another instance</translate>
                  <template v-if="$store.state.instance.instanceUrl !== '/'">
                    <br>
                    ({{ $store.state.instance.instanceUrl }})
                  </template>
                </a>
              </div>
            </div>
            <div class="ten wide column">
              <h4 v-translate class="ui header">About Funkwhale</h4>
              <p>
                <translate>Funkwhale is a free and open-source project run by volunteers. You can help us improve the platform by reporting bugs, suggesting features and share the project with your friends!</translate>
              </p>
              <p>
                <translate>The funkwhale logo was kindly designed and provided by Francis Gading.</translate>
              </p>
            </div>
            <div class="three wide column">
              <h4 v-translate class="ui header">Options</h4>
              <div class="ui form">
                <div class="ui field">
                  <label><translate>Change language</translate></label>
                  <select class="ui dropdown" v-model="$language.current">
                    <option v-for="(language, key) in $language.available" :value="key">{{ language }}</option>
                  </select>
                </div>
              </div>
              <br>
              <a target="_blank" href="https://translate.funkwhale.audio/engage/funkwhale/">
                <translate>Help us translate Funkwhale</translate>
              </a>
            </div>

          </div>
        </div>
      </div>
      <raven
        v-if="$store.state.instance.settings.raven.front_enabled.value"
        :dsn="$store.state.instance.settings.raven.front_dsn.value">
      </raven>
      <playlist-modal v-if="$store.state.auth.authenticated"></playlist-modal>
    </template>
  </div>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'
import {mapState} from 'vuex'
import { WebSocketBridge } from 'django-channels'


import translations from '@/translations'

import Sidebar from '@/components/Sidebar'
import Raven from '@/components/Raven'
import ServiceMessages from '@/components/ServiceMessages'

import PlaylistModal from '@/components/playlists/PlaylistModal'

export default {
  name: 'app',
  components: {
    Sidebar,
    Raven,
    PlaylistModal,
    ServiceMessages
  },
  data () {
    return {
      bridge: null,
      nodeinfo: null,
      instanceUrl: null
    }
  },
  created () {
    this.openWebsocket()
    let self = this
    this.autodetectLanguage()
    setInterval(() => {
      // used to redraw ago dates every minute
      self.$store.commit('ui/computeLastDate')
    }, 1000 * 60)
    if (!this.$store.state.instance.instanceUrl) {
      let defaultInstanceUrl = process.env.VUE_APP_INSTANCE_URL || this.$store.getters['instance/defaultUrl']()
      this.$store.commit('instance/instanceUrl', defaultInstanceUrl)
    } else {
      // needed to trigger initialization of axios
      this.$store.commit('instance/instanceUrl', this.$store.state.instance.instanceUrl)
    }
    this.$store.dispatch('auth/check')
    this.$store.dispatch('instance/fetchSettings')
    this.fetchNodeInfo()
    this.$store.commit('ui/addWebsocketEventHandler', {
      eventName: 'inbox.item_added',
      id: 'sidebarCount',
      handler: this.incrementNotificationCountInSidebar
    })
  },
  destroyed () {
    this.$store.commit('ui/removeWebsocketEventHandler', {
      eventName: 'inbox.item_added',
      id: 'sidebarCount',
    })
    this.disconnect()
  },
  methods: {
    incrementNotificationCountInSidebar (event) {
      this.$store.commit('ui/incrementNotifications', {type: 'inbox', count: 1})
    },
    fetchNodeInfo () {
      let self = this
      axios.get('instance/nodeinfo/2.0/').then(response => {
        self.nodeinfo = response.data
      })
    },
    switchInstance () {
      let confirm = window.confirm(this.$gettext('This will erase your local data and disconnect you, do you want to continue?'))
      if (confirm) {
        this.$store.commit('instance/instanceUrl', null)
      }
    },
    autodetectLanguage () {
      let userLanguage = navigator.language || navigator.userLanguage
      let available = _.keys(translations)
      let matching = available.filter((a) => {
        return userLanguage.replace('-', '_') === a
      })
      let almostMatching = available.filter((a) => {
        return userLanguage.replace('-', '_').split('_')[0] === a.split('_')[0]
      })
      if (matching.length > 0) {
        this.$language.current = matching[0]
      } else if (almostMatching.length > 0) {
        this.$language.current = almostMatching[0]
      }
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
      let url = this.$store.getters['instance/absoluteUrl'](`api/v1/activity?token=${token}`)
      url = url.replace('http://', 'ws://')
      url = url.replace('https://', 'wss://')
      bridge.connect(
        url,
        null,
        {reconnectInterval: 5000})
      bridge.listen(function (event) {
        self.$store.dispatch('ui/websocketEvent', event)
      })
      bridge.socket.addEventListener('open', function () {
        console.log('Connected to WebSocket')
      })
    }
  },
  computed: {
    ...mapState({
      messages: state => state.ui.messages
    }),
    suggestedInstances () {
      let instances = [this.$store.getters['instance/defaultUrl'](), 'https://demo.funkwhale.audio']
      return instances
    },
    version () {
      if (!this.nodeinfo) {
        return null
      }
      return _.get(this.nodeinfo, 'software.version')
    },
    customStylesheets () {
      if (this.$store.state.instance.frontSettings) {
        return this.$store.state.instance.frontSettings.additionalStylesheets || []
      }
    }
  },
  watch: {
    '$store.state.instance.instanceUrl' () {
      this.$store.dispatch('instance/fetchSettings')
      this.fetchNodeInfo()
    },
    '$store.state.auth.authenticated' (newValue) {
      if (!newValue) {
        this.disconnect()
      } else {
        this.openWebsocket()
      }
    },
    '$language.current' (newValue) {
      this.$store.commit('ui/currentLanguage', newValue)
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

.instance-chooser {
  margin-top: 2em;
}

.main.pusher, .footer {
  @include media(">desktop") {
    margin-left: 350px !important;
    margin-top: 50px;
  }
  transform: none !important;
}


.main.pusher > .ui.secondary.menu {
  margin-left: 0;
  margin-right: 0;
  border: none;
  box-shadow: inset 0px -2px 0px 0px rgba(34, 36, 38, 0.15);
  .ui.item {
    border: none;
    border-bottom-style: none;
    margin-bottom: 0px;
    &.active {
      box-shadow: inset 0px -2px 0px 0px #000;
    }
  }
  @include media(">tablet") {
    padding: 0 2.5rem;
  }
  @include media(">desktop") {
    position: fixed;
    left: 350px;
    right: 0px;
    top: 0px;
    z-index: 99;
  }
  background-color: white;
  .item {
    padding-top: 1.5em;
    padding-bottom: 1.5em;
  }
}

.service-messages {
  position: fixed;
  bottom: 1em;
  left: 1em;
  @include media(">desktop") {
    left: 350px;
  }
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

.ellipsis {
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
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

.discrete {
  color: rgba(0, 0, 0, 0.87);
}
.link {
  cursor: pointer;
}

.floated.buttons .button ~ .dropdown {
  border-left: none;
}

.ui.icon.header .circular.icon {
  display: flex;
  justify-content: center;

}

.segment-content .button{
  margin:  0.5em;
}

a {
  cursor: pointer;
}
.segment.hidden {
  display: none;
}

</style>
