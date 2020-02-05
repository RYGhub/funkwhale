<template>
  <router-link :to="url" :title="actor.full_username">
    <template v-if="avatar"><actor-avatar :actor="actor" />&nbsp;</template>{{ repr | truncate(30) }}
  </router-link>
</template>

<script>
import {hashCode, intToRGB} from '@/utils/color'

export default {
  props: {
    actor: {type: Object},
    avatar: {type: Boolean, default: true},
    admin: {type: Boolean, default: false},
    displayName: {type: Boolean, default: false},
  },
  computed: {
    url () {
      if (this.actor.is_local) {
        return {name: 'profile.overview', params: {username: this.actor.preferred_username}}
      } else {
        return {name: 'profile.overview', params: {username: this.actor.full_username}}
      }
    },
    repr () {
      if (this.displayName) {
        return this.actor.preferred_username
      } else {
        return this.actor.full_username
      }
    }
  }
}
</script>
