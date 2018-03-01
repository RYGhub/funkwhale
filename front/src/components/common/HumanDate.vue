<template>
  <time :datetime="date" :title="date | moment">{{ realDate | ago }}</time>
</template>
<script>
import {mapState} from 'vuex'
export default {
  props: ['date'],
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
