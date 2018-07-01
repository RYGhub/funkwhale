<template>
  <div v-title="labels.title">
    <div class="ui vertical stripe segment">
      <h2 class="ui header"><translate>Browsing federated tracks</translate></h2>
      <div class="ui hidden divider"></div>
      <library-track-table :show-library="true"></library-track-table>
    </div>
  </div>
</template>

<script>
import LibraryTrackTable from '@/components/federation/LibraryTrackTable'

export default {
  components: {
    LibraryTrackTable
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Federated tracks')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
