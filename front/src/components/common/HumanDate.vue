<template>
  <time :datetime="date" :title="date | moment">
    <i v-if="icon" class="outline clock icon"></i>
    {{ realDate | ago($store.state.ui.momentLocale) }}
  </time>
</template>
<script>
import {mapState} from 'vuex'
export default {
  props: {
    date: {required: true},
    icon: {type: Boolean, required: false, default: false},
  },
  computed: {
    ...mapState({
      lastDate: state => state.ui.lastDate
    }),
    realDate () {
      if (this.lastDate) {
        // dummy code to trigger a recompute to update the ago render
      }
      return this.date
    }
  }
}
</script>
