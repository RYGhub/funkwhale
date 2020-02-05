<template>
  <time :datetime="`${duration}s`">
    <template v-if="durationObj.hours">{{ durationObj.hours|padDuration }}</template>{{ durationObj.minutes|padDuration }}:{{ durationObj.seconds|padDuration }}
  </time>

</template>
<script>
import {secondsToObject} from '@/filters'

export default {
  props: {
    duration: {required: true},
  },
  computed: {
    durationObj () {
      return secondsToObject(this.duration)
    }
  }
}
</script>
