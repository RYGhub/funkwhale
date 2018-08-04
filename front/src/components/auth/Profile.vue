<template>
  <div class="main pusher" v-title="labels.usernameProfile">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="profile">
      <div :class="['ui', 'head', 'vertical', 'center', 'aligned', 'stripe', 'segment']">
        <h2 class="ui center aligned icon header">
          <i v-if="!profile.avatar.square_crop" class="circular inverted user green icon"></i>
          <img class="ui big circular image" v-else :src="$store.getters['instance/absoluteUrl'](profile.avatar.square_crop)" />
          <div class="content">
            {{ profile.username }}
            <div class="sub header" v-translate="{date: signupDate}">Registered since %{ date }</div>
          </div>
        </h2>
        <div class="ui basic green label">
          <translate>This is you!</translate>
        </div>
        <a v-if="profile.is_staff"
          class="ui yellow label"
          :href="$store.getters['instance/absoluteUrl']('/api/admin')"
          target="_blank">
          <i class="star icon"></i>
          <translate>Staff member</translate>
        </a>
        <router-link class="ui tiny basic button" :to="{path: '/settings'}">
          <i class="setting icon"></i>
          <translate>Settings...</translate>
        </router-link>

      </div>
    </template>
  </div>
</template>

<script>
import {mapState} from 'vuex'

const dateFormat = require('dateformat')

export default {
  props: ['username'],
  created () {
    this.$store.dispatch('auth/fetchProfile')
  },
  computed: {

    ...mapState({
      profile: state => state.auth.profile
    }),
    labels () {
      let msg = this.$gettext('%{ username }\'s profile')
      let usernameProfile = this.$gettextInterpolate(msg, {username: this.username})
      return {
        usernameProfile
      }
    },
    signupDate () {
      let d = new Date(this.profile.date_joined)
      return dateFormat(d, 'longDate')
    },
    isLoading () {
      return !this.profile
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.ui.header > img.image {
  width: 8em;
}
</style>
