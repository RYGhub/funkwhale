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
  </div>
</template>

<script>
import Sidebar from '@/components/Sidebar'

export default {
  name: 'app',
  components: { Sidebar }
}
</script>

<style lang="scss">
// we do the import here instead in main.js
// as resolve order is not deterministric in webpack
// and we end up with CSS rules not applied,
// see https://github.com/webpack/webpack/issues/215
@import 'semantic/semantic.css';


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
#footer {
  padding: 4em;
}
.ui.stripe.segment {
  padding: 4em;
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
