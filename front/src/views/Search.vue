<template>
  <main class="main pusher" v-title="labels.title">
    <section class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>{{ labels.title }}</h2>
        <remote-search-form :initial-id="initialId" :type="type"></remote-search-form>
      </div>
    </section>
  </main>
</template>

<script>
import RemoteSearchForm from '@/components/RemoteSearchForm'

export default {
  props: {
    initialId: { type: String, required: false},
    type: { type: String, required: false},
  },
  components: {
    RemoteSearchForm,
  },
  computed: {
    labels() {
      let title = this.$pgettext('Head/Fetch/Title', "Search a remote object")
      if (this.type === "rss") {
        title = this.$pgettext('Head/Fetch/Title', "Subscribe to a podcast RSS feed")
      }
      return {
        title,
      }
    },
  },
}
</script>
