<template>
  <div v-title="'Federated tracks'">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">Browsing federated tracks</h2>
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
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
