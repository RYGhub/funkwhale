<template>
  <div class="raven"></div>
</template>

<script>
import Raven from 'raven-js'
import RavenVue from 'raven-js/plugins/vue'
import Vue from 'vue'
import logger from '@/logging'

export default {
  props: ['dsn'],
  created () {
    Raven.uninstall()
    this.setUp()
  },
  destroyed () {
    Raven.uninstall()
  },
  methods: {
    setUp () {
      Raven.uninstall()
      logger.default.info('Installing raven...')
      Raven.config(this.dsn).addPlugin(RavenVue, Vue).install()
    }
  },
  watch: {
    dsn: function () {
      this.setUp()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped >
.raven {
  display: none;
}
</style>
