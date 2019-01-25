<template>
  <div id="app">
    <!-- here, we display custom stylesheets, if any -->
    <link
      v-for="url in customStylesheets"
      rel="stylesheet"
      property="stylesheet"
      :href="url"
      :key="url"
    >
    <div class="ui main text container instance-chooser" v-if="!$store.state.instance.instanceUrl">
      <div class="ui padded segment">
        <h1 class="ui header">
          <translate>Choose your instance</translate>
        </h1>
        <form class="ui form" @submit.prevent="$store.dispatch('instance/setUrl', instanceUrl)">
          <p>
            <translate>You need to select an instance in order to continue</translate>
          </p>
          <div class="ui action input">
            <input type="text" v-model="instanceUrl">
            <button type="submit" class="ui button">
              <translate>Submit</translate>
            </button>
          </div>
          <p>
            <translate>Suggested choices</translate>
          </p>
          <div class="ui bulleted list">
            <div class="ui item" v-for="url in suggestedInstances">
              <a @click="instanceUrl = url; $store.dispatch('instance/setUrl', url)">{{ url }}</a>
            </div>
          </div>
        </form>
      </div>
    </div>
    <template v-else>
      <sidebar></sidebar>
      <service-messages v-if="messages.length > 0"/>
      <router-view :key="$route.fullPath"></router-view>
      <div class="ui fitted divider"></div>
      <app-footer
        :version="version"
        @show:shortcuts-modal="showShortcutsModal = !showShortcutsModal"
      ></app-footer>
      <playlist-modal v-if="$store.state.auth.authenticated"></playlist-modal>
      <shortcuts-modal @update:show="showShortcutsModal = $event" :show="showShortcutsModal"></shortcuts-modal>
      <GlobalEvents @keydown.h.exact="showShortcutsModal = !showShortcutsModal"/>
    </template>
  </div>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import _ from '@/lodash'
import {mapState} from 'vuex'
import { WebSocketBridge } from 'django-channels'
import GlobalEvents from '@/components/utils/global-events'
import Sidebar from '@/components/Sidebar'
import AppFooter from '@/components/Footer'
import ServiceMessages from '@/components/ServiceMessages'
import moment from  'moment'
import locales from './locales'
import PlaylistModal from '@/components/playlists/PlaylistModal'
import ShortcutsModal from '@/components/ShortcutsModal'

export default {
  name: 'app',
  components: {
    Sidebar,
    AppFooter,
    PlaylistModal,
    ShortcutsModal,
    GlobalEvents,
    ServiceMessages
  },
  data () {
    return {
      bridge: null,
      nodeinfo: null,
      instanceUrl: null,
      showShortcutsModal: false,
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
      // we have several way to guess the API server url. By order of precedence:
      // 1. use the url provided in settings.json, if any
      // 2. use the url specified when building via VUE_APP_INSTANCE_URL
      // 3. use the current url
      let defaultInstanceUrl = this.$store.state.instance.frontSettings.defaultServerUrl || process.env.VUE_APP_INSTANCE_URL || this.$store.getters['instance/defaultUrl']()
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
      let available = locales.locales.map(e => { return e.code })
      let self = this
      let candidate
      let matching = available.filter((a) => {
        return userLanguage.replace('-', '_') === a
      })
      let almostMatching = available.filter((a) => {
        return userLanguage.replace('-', '_').split('_')[0] === a.split('_')[0]
      })
      if (matching.length > 0) {
        candidate = matching[0]
      } else if (almostMatching.length > 0) {
        candidate = almostMatching[0]
      } else {
        return
      }
      this.$store.commit('ui/currentLanguage', candidate)
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
        [],
        {reconnectInterval: 1000 * 60})
      bridge.listen(function (event) {
        self.$store.dispatch('ui/websocketEvent', event)
      })
      bridge.socket.addEventListener('open', function () {
        console.log('Connected to WebSocket')
      })
    },
  },
  computed: {
    ...mapState({
      messages: state => state.ui.messages
    }),
    suggestedInstances () {
      let instances = this.$store.state.instance.knownInstances.slice(0)
      console.log('instance', instances)
      if (this.$store.state.instance.frontSettings.defaultServerUrl) {
        let serverUrl = this.$store.state.instance.frontSettings.defaultServerUrl
        if (!serverUrl.endsWith('/')) {
          serverUrl = serverUrl + '/'
        }
        instances.push(serverUrl)
      }
      instances.push(this.$store.getters['instance/defaultUrl'](), 'https://demo.funkwhale.audio/')
      console.log('HELLO', instances)
      return _.uniq(instances.filter((e) => {return e}))
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
    '$store.state.ui.currentLanguage': {
      immediate: true,
      handler(newValue) {
        let self = this
        import(`./translations/${newValue}.json`).then((response) =>{
          Vue.$translations[newValue] = response.default[newValue]
        }).finally(() => {
          // set current language twice, otherwise we seem to have a cache somewhere
          // and rendering does not happen
          self.$language.current = 'noop'
          self.$language.current = newValue
        })
        if (newValue === 'en_US') {
          return self.$store.commit('ui/momentLocale', 'en')
        }
        let momentLocale = newValue.replace('_', '-').toLowerCase()
        import(`moment/locale/${momentLocale}.js`).then(() => {
          self.$store.commit('ui/momentLocale', momentLocale)
        }).catch(() => {
          console.log('No momentjs locale available for', momentLocale)
          let shortLocale = momentLocale.split('-')[0]
          import(`moment/locale/${shortLocale}.js`).then(() => {
            self.$store.commit('ui/momentLocale', shortLocale)
          }).catch(() => {
            console.log('No momentjs locale available for', shortLocale)
          })
        })
        console.log(moment.locales())
      }
    }
  }
}
</script>

<style lang="scss">
@import "style/_main";
</style>
