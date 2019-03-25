<template>
  <main class="main pusher" v-title="labels.title">
    <div class="ui vertical stripe segment">
      <section class="ui text container">
        <router-link :to="{name: 'settings'}">
          <translate translate-context="Content/Applications/Link">Back to settings</translate>
        </router-link>
        <h2 class="ui header">
          <translate translate-context="Content/Applications/Title">Create a new application</translate>
        </h2>
        <application-form
          @created="$router.push({name: 'settings.applications.edit', params: {id: $event.client_id}})" />
      </section>
    </div>
  </main>
</template>

<script>
import ApplicationForm from "@/components/auth/ApplicationForm"

export default {
  components: {
    ApplicationForm
  },
   data() {
    return {
      application: null,
      isLoading: false,
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('Content/Applications/Title', "Create a new application")
      }
    },
  }
}
</script>
