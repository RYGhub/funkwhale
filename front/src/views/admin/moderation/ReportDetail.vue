<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">

      <div class="ui vertical stripe segment">
        <report-card :obj="object"></report-card>
      </div>
    </template>
  </main>
</template>

<script>
import axios from "axios"

import ReportCard from "@/components/manage/moderation/ReportCard"

export default {
  props: ["id"],
  components: {
    ReportCard,
  },
  data() {
    return {
      isLoading: true,
      object: null,
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      let url = `manage/moderation/reports/${this.id}/`
      axios.get(url).then(response => {
        self.object = response.data
        self.isLoading = false
      })
    },
  },
}
</script>
