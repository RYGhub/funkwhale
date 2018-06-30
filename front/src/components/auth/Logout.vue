<template>
  <div class="main pusher" v-title="'Log Out'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>
          {{ $gettext('Are you sure you want to log out?') }}
        </h2>
        <p v-translate="{username: $store.state.auth.username}">You are currently logged in as %{ username }</p>
        <button class="ui button" @click="$store.dispatch('auth/logout')">{{ $gettext('Yes, log me out!') }}</button>
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
