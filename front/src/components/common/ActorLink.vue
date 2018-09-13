<template>
  <span :title="actor.full_username">
    <actor-avatar v-if="avatar" :actor="actor" />
    &nbsp;{{ actor.full_username | truncate(30) }}
  </span>
</template>

<script>
import {hashCode, intToRGB} from '@/utils/color'

export default {
  props: {
    actor: {type: Object},
    avatar: {type: Boolean, default: true}
  }
}
</script>
