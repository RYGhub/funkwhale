<template>
  <div id="app" :key="String($store.state.instance.instanceUrl)">
    <!-- here, we display custom stylesheets, if any -->
    <link
      v-for="url in customStylesheets"
      rel="stylesheet"
      property="stylesheet"
      :href="url"
      :key="url"
    >
    <template>
      <sidebar></sidebar>
      <set-instance-modal @update:show="showSetInstanceModal = $event" :show="showSetInstanceModal"></set-instance-modal>
      <service-messages v-if="messages.length > 0"/>
      <router-view :key="$route.fullPath"></router-view>
      <div class="ui fitted divider"></div>
      <app-footer
        :version="version"
        @show:shortcuts-modal="showShortcutsModal = !showShortcutsModal"
        @show:set-instance-modal="showSetInstanceModal = !showSetInstanceModal"
      ></app-footer>
      <playlist-modal v-if="$store.state.auth.authenticated"></playlist-modal>
      <filter-modal v-if="$store.state.auth.authenticated"></filter-modal>
      <report-modal></report-modal>
      <shortcuts-modal @update:show="showShortcutsModal = $event" :show="showShortcutsModal"></shortcuts-modal>
      <GlobalEvents @keydown.h.exact="showShortcutsModal = !showShortcutsModal"/>
    </template>
  </div>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import _ from '@/lodash'
import {mapState, mapGetters} from 'vuex'
import { WebSocketBridge } from 'django-channels'
import GlobalEvents from '@/components/utils/global-events'
import Sidebar from '@/components/Sidebar'
import AppFooter from '@/components/Footer'
import ServiceMessages from '@/components/ServiceMessages'
import moment from  'moment'
import locales from './locales'
import PlaylistModal from '@/components/playlists/PlaylistModal'
import FilterModal from '@/components/moderation/FilterModal'
import ReportModal from '@/components/moderation/ReportModal'
import ShortcutsModal from '@/components/ShortcutsModal'
import SetInstanceModal from '@/components/SetInstanceModal'

export default {
  name: 'app',
  components: {
    Sidebar,
    AppFooter,
    FilterModal,
    ReportModal,
    PlaylistModal,
    ShortcutsModal,
    GlobalEvents,
    ServiceMessages,
    SetInstanceModal,
  },
  data () {
    return {
      bridge: null,
      instanceUrl: null,
      showShortcutsModal: false,
      showSetInstanceModal: false,
    }
  },
  async created () {
    this.openWebsocket()
    let self = this
    if (!this.$store.state.ui.selectedLanguage) {
      this.autodetectLanguage()
    }
    setInterval(() => {
      // used to redraw ago dates every minute
      self.$store.commit('ui/computeLastDate')
    }, 1000 * 60)
    const urlParams = new URLSearchParams(window.location.search);
    const serverUrl = urlParams.get('_server')
    if (serverUrl) {
      this.$store.commit('instance/instanceUrl', serverUrl)
    }
    else if (!this.$store.state.instance.instanceUrl) {
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
    await this.fetchNodeInfo()
    this.$store.dispatch('auth/check')
    this.$store.dispatch('instance/fetchSettings')
    this.$store.commit('ui/addWebsocketEventHandler', {
      eventName: 'inbox.item_added',
      id: 'sidebarCount',
      handler: this.incrementNotificationCountInSidebar
    })
    this.$store.commit('ui/addWebsocketEventHandler', {
      eventName: 'mutation.created',
      id: 'sidebarReviewEditCount',
      handler: this.incrementReviewEditCountInSidebar
    })
    this.$store.commit('ui/addWebsocketEventHandler', {
      eventName: 'mutation.updated',
      id: 'sidebarReviewEditCount',
      handler: this.incrementReviewEditCountInSidebar
    })
    this.$store.commit('ui/addWebsocketEventHandler', {
      eventName: 'report.created',
      id: 'sidebarPendingReviewReportCount',
      handler: this.incrementPendingReviewReportsCountInSidebar
    })
  },
  mounted () {
    let self = this

    // slight hack to allow use to have internal links in <translate> tags
    // while preserving router behaviour
    document.documentElement.addEventListener('click', function (event) {
      if (!event.target.matches('a.internal')) return;
      self.$router.push(event.target.getAttribute('href'))
      event.preventDefault();
    }, false);

  },
  destroyed () {
    this.$store.commit('ui/removeWebsocketEventHandler', {
      eventName: 'inbox.item_added',
      id: 'sidebarCount',
    })
    this.$store.commit('ui/removeWebsocketEventHandler', {
      eventName: 'mutation.created',
      id: 'sidebarReviewEditCount',
    })
    this.$store.commit('ui/removeWebsocketEventHandler', {
      eventName: 'mutation.updated',
      id: 'sidebarReviewEditCount',
    })
    this.$store.commit('ui/removeWebsocketEventHandler', {
      eventName: 'mutation.updated',
      id: 'sidebarPendingReviewReportCount',
    })
    this.disconnect()
  },
  methods: {
    incrementNotificationCountInSidebar (event) {
      this.$store.commit('ui/incrementNotifications', {type: 'inbox', count: 1})
    },
    incrementReviewEditCountInSidebar (event) {
      this.$store.commit('ui/incrementNotifications', {type: 'pendingReviewEdits', value: event.pending_review_count})
    },
    incrementPendingReviewReportsCountInSidebar (event) {
      this.$store.commit('ui/incrementNotifications', {type: 'pendingReviewReports', value: event.unresolved_count})
    },
    async fetchNodeInfo () {
      let response = await axios.get('instance/nodeinfo/2.0/')
      this.$store.commit('instance/nodeinfo', response.data)
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
    getTrackInformationText(track) {
      const trackTitle = track.title
      const artistName = (
        (track.artist) ? track.artist.name : track.album.artist.name)
      const text = `♫ ${trackTitle} – ${artistName} ♫`
      return text
    },
    updateDocumentTitle() {
      let parts = []
      const currentTrackPart = (
        (this.currentTrack) ? this.getTrackInformationText(this.currentTrack)
        : null)
      if (currentTrackPart) {
        parts.push(currentTrackPart)
      }
      if (this.$store.state.ui.pageTitle) {
        parts.push(this.$store.state.ui.pageTitle)
      }
      parts.push(this.$store.state.instance.settings.instance.name.value || 'Funkwhale')
      document.title = parts.join(' – ')
    },
  },
  computed: {
    ...mapState({
      messages: state => state.ui.messages,
      nodeinfo: state => state.instance.nodeinfo,
    }),
    ...mapGetters({
      currentTrack: 'queue/currentTrack'
    }),
    suggestedInstances () {
      let instances = this.$store.state.instance.knownInstances.slice(0)
      if (this.$store.state.instance.frontSettings.defaultServerUrl) {
        let serverUrl = this.$store.state.instance.frontSettings.defaultServerUrl
        if (!serverUrl.endsWith('/')) {
          serverUrl = serverUrl + '/'
        }
        instances.push(serverUrl)
      }
      instances.push(this.$store.getters['instance/defaultUrl'](), 'https://demo.funkwhale.audio/')
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
    '$store.state.ui.theme': {
      immediate: true,
      handler (newValue, oldValue) {
        let oldTheme = oldValue || 'light'
        document.body.classList.remove(`theme-${oldTheme}`)
        document.body.classList.add(`theme-${newValue}`)
      },
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
      }
    },
    'currentTrack': {
      immediate: true,
      handler(newValue) {
        this.updateDocumentTitle()
      },
    },
    '$store.state.ui.pageTitle': {
      immediate: true,
      handler(newValue) {
        this.updateDocumentTitle()
      },
    },
  }
}
</script>

<style lang="scss">
@import "style/_main";
</style>
