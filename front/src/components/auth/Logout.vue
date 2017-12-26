<template>
  <div class="main pusher">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>Are you sure you want to log out?</h2>
        <p>You are currently logged in as {{ $store.state.auth.username }}</p>
        <button class="ui button" @click="$store.dispatch('auth/logout')">Yes, log me out!</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'logout'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
