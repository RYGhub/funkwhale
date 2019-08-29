<template>
  <router-link :to="{name: 'manage.moderation.accounts.detail', params: {id: actor.full_username}}" v-if="admin" :title="actor.full_username">
    <actor-avatar v-if="avatar" :actor="actor" />
    &nbsp;{{ actor.full_username | truncate(30) }}
  </router-link>
  <span v-else :title="actor.full_username">
    <actor-avatar v-if="avatar" :actor="actor" />
    &nbsp;{{ actor.full_username | truncate(30) }}
  </span>
</template>

<script>
import {hashCode, intToRGB} from '@/utils/color'

export default {
  props: {
    actor: {type: Object},
    avatar: {type: Boolean, default: true},
    admin: {type: Boolean, default: false},
  }
}
</script>
