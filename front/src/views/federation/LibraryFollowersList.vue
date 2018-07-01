<template>
  <div v-title="labels.title">
    <div class="ui vertical stripe segment">
      <h2 class="ui header"><translate>Browsing followers</translate></h2>
      <p>
        <translate>Be careful when accepting follow requests, as it means the follower will have access to your entire library.</translate>
      </p>
      <div class="ui hidden divider"></div>
      <library-follow-table></library-follow-table>
    </div>
  </div>
</template>

<script>
import LibraryFollowTable from '@/components/federation/LibraryFollowTable'

export default {
  components: {
    LibraryFollowTable
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Followers')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
