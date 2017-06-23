<template>
  <div id="app">
    <sidebar></sidebar>
    <router-view></router-view>
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
.main.pusher {
  margin-left: 350px !important;
  transform: none !important;
  padding: 1.5rem 0;
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
