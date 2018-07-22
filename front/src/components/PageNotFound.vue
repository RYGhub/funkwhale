<template>
  <div class="main pusher" :v-title="labels.title">
    <div class="ui vertical stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
          <i class="warning icon"></i>
          <div class="content">
            <translate>Page not found!</translate>
          </div>
        </h1>
        <p><translate>We're sorry, the page you asked for does not exist:</translate></p>
        <a :href="path">{{ path }}</a>
        <div class="ui hidden divider"></div>
        <router-link class="ui icon button" to="/">
          <translate>Go to home page</translate>
          <i class="right arrow icon"></i>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data: function () {
    return {
      path: window.location.href
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Page Not Found')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
