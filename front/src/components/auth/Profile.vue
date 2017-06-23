<template>
  <div class="main pusher">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="profile">
      <div :class="['ui', 'head', 'vertical', 'center', 'aligned', 'stripe', 'segment']">
        <h2 class="ui center aligned icon header">
          <i class="circular inverted user green icon"></i>
          <div class="content">
            {{ profile.username }}
            <div class="sub header">Registered since {{ signupDate }}</div>
          </div>
        </h2>
        <div class="ui basic green label">this is you!</div>
        <div v-if="profile.is_staff" class="ui yellow label">
          <i class="star icon"></i>
          Staff member
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import auth from '@/auth'
var dateFormat = require('dateformat')

export default {
  name: 'login',
  props: ['username'],
  data () {
    return {
      profile: null
    }
  },
  created () {
    this.fetchProfile()
  },
  methods: {
    fetchProfile () {
      let self = this
      auth.fetchProfile().then(data => {
        self.profile = data
      })
    }
  },
  computed: {
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
</style>
