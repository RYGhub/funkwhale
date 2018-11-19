<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header"><translate>Library files</translate></h2>
      <div class="ui hidden divider"></div>
      <library-files-table :show-library="true"></library-files-table>
    </section>
  </main>
</template>

<script>
import LibraryFilesTable from "@/components/manage/library/FilesTable"

export default {
  components: {
    LibraryFilesTable
  },
  computed: {
    labels() {
      return {
        title: this.$gettext("Files")
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
