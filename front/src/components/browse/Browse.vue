<template>
  <div class="main browse pusher">
    <div class="ui secondary pointing menu">
      <router-link class="ui item" to="/browse">Browse</router-link>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>

export default {
  name: 'browse'
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
.browse.pusher > .ui.secondary.menu {
  margin: 0 2.5rem;
}

.browse {
  .ui.segment.head {
    background-size: cover;
    background-position: center;
    padding: 0;
    .segment-content {
      margin: 0 auto;
      padding: 4em;
    }
    &.with-background {
      .header {
        &, .sub, a {
          text-shadow: 0 1px 0 rgba(0, 0, 0, 0.8);
          color: white !important;
        }
      }
      .segment-content {
        background-color: rgba(0, 0, 0, 0.5)
      }

    }
  }

}

</style>
