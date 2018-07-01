<template>
  <div class="main pusher" v-title="username + '\'s Profile'">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="$store.state.auth.profile">
      <div :class="['ui', 'head', 'vertical', 'center', 'aligned', 'stripe', 'segment']">
        <h2 class="ui center aligned icon header">
          <i class="circular inverted user green icon"></i>
          <div class="content">
            {{ $store.state.auth.profile.username }}
            <div class="sub header" v-translate="{date: signupDate}">Registered since %{ date }</div>
          </div>
        </h2>
        <div class="ui basic green label">
          <translate>This is you!</translate>
        </div>
        <div v-if="$store.state.auth.profile.is_staff" class="ui yellow label">
          <i class="star icon"></i>
          <translate>Staff member</translate>
        </div>
        <router-link class="ui tiny basic button" :to="{path: '/settings'}">
          <i class="setting icon"> </i>
          <translate>Settings...</translate>
        </router-link>

      </div>
    </template>
  </div>
</template>

<script>
const dateFormat = require('dateformat')

export default {
  name: 'login',
  props: ['username'],
  created () {
    this.$store.dispatch('auth/fetchProfile')
  },
  computed: {
    signupDate () {
      let d = new Date(this.$store.state.auth.profile.date_joined)
      return dateFormat(d, 'longDate')
    },
    isLoading () {
      return !this.$store.state.auth.profile
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
