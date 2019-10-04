<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">{{ labels.title }}</h2>
      <div class="ui hidden divider"></div>
      <libraries-table :update-url="true" :default-query="defaultQuery"></libraries-table>
    </section>
  </main>
</template>

<script>
import LibrariesTable from "@/components/manage/library/LibrariesTable"

export default {
  components: {
    LibrariesTable
  },
  props: {
    defaultQuery: {type: String, required: false},
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*/Noun', 'Libraries')
      }
    }
  }
}
</script>
