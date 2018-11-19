<template>
  <section class="ui vertical aligned stripe segment">
    <library-files-table :default-query="query"></library-files-table>
  </section>
</template>

<script>
import LibraryFilesTable from "./FilesTable"

export default {
  props: ["query"],
  components: {
    LibraryFilesTable
  }
}
</script>
