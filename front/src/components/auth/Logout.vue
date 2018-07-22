<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>
          <translate>Are you sure you want to log out?</translate>
        </h2>
        <p v-translate="{username: $store.state.auth.username}">You are currently logged in as %{ username }</p>
        <button class="ui button" @click="$store.dispatch('auth/logout')"><translate>Yes, log me out!</translate></button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    labels () {
      return {
        title: this.$gettext('Log Out')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
