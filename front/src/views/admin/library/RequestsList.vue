<template>
  <div v-title="$gettext('Import requests')">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">{{ $gettext('Import requests') }}</h2>
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
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
