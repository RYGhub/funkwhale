<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">{{ labels.title }}</h2>
      <div class="ui hidden divider"></div>
      <tags-table :update-url="true" :default-query="defaultQuery"></tags-table>
    </section>
  </main>
</template>

<script>
import TagsTable from "@/components/manage/library/TagsTable"

export default {
  components: {
    TagsTable
  },
  props: {
    defaultQuery: {type: String, required: false},
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*/Noun', 'Tags')
      }
    }
  }
}
</script>
