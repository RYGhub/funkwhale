<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">{{ labels.title }}</h2>
      <div class="ui hidden divider"></div>
      <albums-table :update-url="true" :default-query="defaultQuery"></albums-table>
    </section>
  </main>
</template>

<script>
import AlbumsTable from "@/components/manage/library/AlbumsTable"

export default {
  components: {
    AlbumsTable
  },
  props: {
    defaultQuery: {type: String, required: false},
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*', 'Albums')
      }
    }
  }
}
</script>
