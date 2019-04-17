<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">{{ labels.title }}</h2>
      <div class="ui hidden divider"></div>
      <tracks-table :update-url="true" :default-query="defaultQuery"></tracks-table>
    </section>
  </main>
</template>

<script>
import TracksTable from "@/components/manage/library/TracksTable"

export default {
  components: {
    TracksTable
  },
  props: {
    defaultQuery: {type: String, required: false},
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*', 'Tracks')
      }
    }
  }
}
</script>
