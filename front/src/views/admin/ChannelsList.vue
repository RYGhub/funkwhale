<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">{{ labels.title }}</h2>
      <div class="ui hidden divider"></div>
      <channels-table :update-url="true" :default-query="defaultQuery"></channels-table>
    </section>
  </main>
</template>

<script>
import ChannelsTable from "@/components/manage/ChannelsTable"

export default {
  components: {
    ChannelsTable
  },
  props: {
    defaultQuery: {type: String, required: false},
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('*/*/*', 'Channels')
      }
    }
  }
}
</script>
