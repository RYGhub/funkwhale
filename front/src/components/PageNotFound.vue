<template>
  <div class="main pusher" v-title="'Page Not Found'">
    <div class="ui vertical stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
          <i class="warning icon"></i>
          <div class="content">
            <strike>{{ $t('Whale') }}</strike> {{ $t('Page not found!') }}
          </div>
        </h1>
        <p>{{ $t('We\'re sorry, the page you asked for does not exists.') }}</p>
        <i18next path="Requested URL: {%0%}"><a :href="path">{{ path }}</a></i18next>
        <router-link class="ui icon button" to="/">
          {{ $t('Go to home page') }}
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
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
