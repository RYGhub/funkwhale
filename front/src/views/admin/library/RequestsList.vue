<template>
  <div v-title="labels.importRequests">
    <div class="ui vertical stripe segment">
      <h2 class="ui header"><translate>Import requests</translate></h2>
      <div class="ui hidden divider"></div>
      <library-requests-table></library-requests-table>
    </div>
  </div>
</template>

<script>
import LibraryRequestsTable from '@/components/manage/library/RequestsTable'

export default {
  components: {
    LibraryRequestsTable
  },
  computed: {
    labels () {
      return {
        importRequests: this.$gettext('Import requests')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
