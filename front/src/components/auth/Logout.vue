<template>
  <div class="main pusher" v-title="'Log Out'">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2><i18next path="Are you sure you want to log out?"/></h2>
        <i18next tag="p" path="You are currently logged in as {%0%}">{{ $store.state.auth.username }}</i18next>
        <button class="ui button" @click="$store.dispatch('auth/logout')"><i18next path="Yes, log me out!"/></button>
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
