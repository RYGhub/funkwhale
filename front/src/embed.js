
import Vue from 'vue'
import Embed from './Embed'
import VuePlyr from 'vue-plyr'

Vue.use(VuePlyr)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  template: '<Embed/>',
  components: { Embed }
})
