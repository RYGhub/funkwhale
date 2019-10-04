
import Vue from 'vue'
import EmbedFrame from './EmbedFrame'
import VuePlyr from 'vue-plyr'

Vue.use(VuePlyr)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  render (h) {
    return h('EmbedFrame')
  },
  components: { EmbedFrame }
})
