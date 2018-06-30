<template>
  <div class="main pusher"  v-title="$gettext('Instance settings')">
    <div class="ui vertical stripe segment">
      <div class="ui text container">
        <div :class="['ui', {'loading': isLoading}, 'form']"></div>
        <div id="settings-grid" v-if="settingsData" class="ui grid">
          <div class="twelve wide stretched column">
            <settings-group
              :settings-data="settingsData"
              :group="group"
              :key="group.title"
              v-for="group in groups" />
          </div>
          <div class="four wide column">
            <div class="ui sticky vertical secondary menu">
              <div class="header item">{{ $gettext('Sections') }}</div>
              <a :class="['menu', {active: group.id === current}, 'item']"
                @click.prevent="scrollTo(group.id)"
                :href="'#' + group.id"
                v-for="group in groups">{{ group.label }}</a>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import $ from 'jquery'

import SettingsGroup from '@/components/admin/SettingsGroup'

export default {
  components: {
    SettingsGroup
  },
  data () {
    return {
      isLoading: false,
      settingsData: null,
      current: null
    }
  },
  created () {
    let self = this
    this.fetchSettings().then(r => {
      self.$nextTick(() => {
        if (self.$store.state.route.hash) {
          self.scrollTo(self.$store.state.route.hash.substr(1))
        }
        $('select.dropdown').dropdown()
      })
    })
  },
  methods: {
    scrollTo (id) {
      this.current = id
      document.getElementById(id).scrollIntoView()
    },
    fetchSettings () {
      let self = this
      self.isLoading = true
      return axios.get('instance/admin/settings/').then((response) => {
        self.settingsData = response.data
        self.isLoading = false
      })
    }
  },
  computed: {
    groups () {
      // somehow, extraction fails if in the return block directly
      let instanceLabel = this.$gettext('Instance information')
      let usersLabel = this.$gettext('Users')
      let importsLabel = this.$gettext('Imports')
      let playlistsLabel = this.$gettext('Playlists')
      let federationLabel = this.$gettext('Federation')
      let subsonicLabel = this.$gettext('Subsonic')
      let statisticsLabel = this.$gettext('Statistics')
      let errorLabel = this.$gettext('Error reporting')
      return [
        {
          label: instanceLabel,
          id: 'instance',
          settings: [
            'instance__name',
            'instance__short_description',
            'instance__long_description'
          ]
        },
        {
          label: usersLabel,
          id: 'users',
          settings: [
            'users__registration_enabled',
            'common__api_authentication_required',
            'users__default_permissions'
          ]
        },
        {
          label: importsLabel,
          id: 'imports',
          settings: [
            'providers_youtube__api_key'
          ]
        },
        {
          label: playlistsLabel,
          id: 'playlists',
          settings: [
            'playlists__max_tracks'
          ]
        },
        {
          label: federationLabel,
          id: 'federation',
          settings: [
            'federation__enabled',
            'federation__music_needs_approval',
            'federation__collection_page_size',
            'federation__music_cache_duration',
            'federation__actor_fetch_delay'
          ]
        },
        {
          label: subsonicLabel,
          id: 'subsonic',
          settings: [
            'subsonic__enabled'
          ]
        },
        {
          label: statisticsLabel,
          id: 'statistics',
          settings: [
            'instance__nodeinfo_enabled',
            'instance__nodeinfo_stats_enabled',
            'instance__nodeinfo_private'
          ]
        },
        {
          label: errorLabel,
          id: 'reporting',
          settings: [
            'raven__front_enabled',
            'raven__front_dsn'

          ]
        }
      ]
    }
  },
  watch: {
    settingsData () {
      let self = this
      this.$nextTick(() => {
        $(self.$el).find('.sticky').sticky({context: '#settings-grid'})
      })
    }
  }
}
</script>
