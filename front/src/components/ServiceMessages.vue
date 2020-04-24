<template>
  <div class="ui toast-container">
    <message v-for="message in $store.state.ui.messages" :message="message" :key="message.key"></message>
    <slot></slot>
  </div>
</template>

<script>

export default {}
</script>
