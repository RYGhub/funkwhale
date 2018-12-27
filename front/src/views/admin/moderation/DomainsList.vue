<template>
  <main v-title="labels.domains">
    <section class="ui vertical stripe segment">
      <h2 class="ui header"><translate>Domains</translate></h2>
      <div class="ui hidden divider"></div>
      <domains-table></domains-table>
    </section>
  </main>
</template>

<script>
import DomainsTable from "@/components/manage/moderation/DomainsTable"

export default {
  components: {
    DomainsTable
  },
  computed: {
    labels() {
      return {
        domains: this.$gettext("Domains")
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
