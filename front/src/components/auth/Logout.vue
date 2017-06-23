<template>
  <div class="main pusher">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>Are you sure you want to log out?</h2>
        <p>You are currently logged in as {{ auth.user.username }}</p>
        <button class="ui button" @click="logout">Yes, log me out!</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import auth from '@/auth'

export default {
  name: 'logout',
  data () {
    return {
      // We need to initialize the component with any
      // properties that will be used in it
      auth: auth
    }
  },
  methods: {
    logout () {
      auth.logout()
      this.$router.push({name: 'index'})
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
