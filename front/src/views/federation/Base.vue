<template>
  <div class="main pusher"  v-title="'Federation'">
    <div class="ui secondary pointing menu">
    </div>
    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>
