<template>
  <span :title="actor.full_username">
    <span :style="defaultAvatarStyle" class="ui circular label">{{ actor.preferred_username[0]}}</span>
    &nbsp;{{ actor.full_username | truncate(30) }}
  </span>
</template>

<script>
import {hashCode, intToRGB} from '@/utils/color'

export default {
  props: ['actor'],
  computed: {
    actorColor () {
      return intToRGB(hashCode(this.actor.full_username))
    },
    defaultAvatarStyle () {
      return {
        'background-color': `#${this.actorColor}`
      }
    }
  }
}
</script>
<style scoped>
.tiny.circular.avatar {
  width: 1.7em;
  height: 1.7em;
}
</style>
