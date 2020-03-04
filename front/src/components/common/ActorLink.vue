<template>
  <router-link :to="url" :title="actor.full_username">
    <template v-if="avatar"><actor-avatar :actor="actor" />&nbsp;</template><slot>{{ repr | truncate(truncateLength) }}</slot>
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
    truncateLength: {type: Number, default: 30},
  },
  computed: {
    url () {
      if (this.actor.is_local) {
        return {name: 'profile.overview', params: {username: this.actor.preferred_username}}
      } else {
        return {name: 'profile.full.overview', params: {username: this.actor.preferred_username, domain: this.actor.domain}}
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
