<template>
  <div class="ui vertical aligned stripe segment">
    <library-files-table :default-query="query"></library-files-table>
  </div>
</template>

<script>
import LibraryFilesTable from './FilesTable'

export default {
  props: ['query'],
  components: {
    LibraryFilesTable
  }
}
</script>
