<template>
  <div id="app">
    <sidebar></sidebar>
    <router-view :key="$route.fullPath"></router-view>
    <div class="ui fitted divider"></div>
    <div id="footer" class="ui vertical footer segment">
      <div class="ui container">
        <div class="ui stackable equal height stackable grid">
          <div class="three wide column">
            <i18next tag="h4" class="ui header" path="Links"></i18next>
            <div class="ui link list">
              <router-link class="item" to="/about">
                <i18next path="About this instance" />
              </router-link>
              <i18next tag="a" href="https://funkwhale.audio" class="item" target="_blank" path="Official website" />
              <i18next tag="a" href="https://docs.funkwhale.audio" class="item" target="_blank" path="Documentation" />
              <i18next tag="a" href="https://code.eliotberriot.com/funkwhale/funkwhale" class="item" target="_blank" path="Source code" />
              <i18next tag="a" href="https://code.eliotberriot.com/funkwhale/funkwhale/issues" class="item" target="_blank" path="Issue tracker" />
            </div>
          </div>
          <div class="ten wide column">
            <i18next tag="h4" class="ui header" path="About funkwhale" />
            <p>
              <i18next path="Funkwhale is a free and open-source project run by volunteers. You can help us improve the platform by reporting bugs, suggesting features and share the project with your friends!"/>
            </p>
            <p>
              <i18next path="The funkwhale logo was kindly designed and provided by Francis Gading."/>
            </p>
          </div>
        </div>
      </div>
    </div>
    <raven
      v-if="$store.state.instance.settings.raven.front_enabled.value"
      :dsn="$store.state.instance.settings.raven.front_dsn.value">
    </raven>
    <playlist-modal v-if="$store.state.auth.authenticated"></playlist-modal>
  </div>
</template>

<script>
import Sidebar from '@/components/Sidebar'
import Raven from '@/components/Raven'

import PlaylistModal from '@/components/playlists/PlaylistModal'

export default {
  name: 'app',
  components: {
    Sidebar,
    Raven,
    PlaylistModal
  },
  created () {
    this.$store.dispatch('instance/fetchSettings')
    let self = this
    setInterval(() => {
      // used to redraw ago dates every minute
      self.$store.commit('ui/computeLastDate')
    }, 1000 * 60)
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
