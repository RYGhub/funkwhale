<template>
  <section class="ui vertical aligned stripe segment" v-title="labels.title">
    <div class="ui text container">
      <h1>{{ labels.title }}</h1>
      <p><translate>There are various ways to grab new content and make it available here.</translate></p>
      <div class="ui segment">
        <h2><translate>Upload audio content</translate></h2>
        <p><translate>Upload music files (MP3, OGG, FLAC, etc.) from your personal library directly from your browser to enjoy them here.</translate></p>
        <p>
          <strong><translate :translate-params="{quota: defaultQuota}">This instance offers up to %{quota} of storage space for every user.</translate></strong>
        </p>
        <router-link :to="{name: 'content.libraries.index'}" class="ui green button">
          <translate>Get started</translate>
        </router-link>
      </div>
      <div class="ui segment">
        <h2><translate>Follow remote libraries</translate></h2>
        <p><translate>You can follow libraries from other users to get access to new music. Public libraries can be followed immediatly, while following a private library requires approval from its owner.</translate></p>
        <router-link :to="{name: 'content.remote.index'}" class="ui green button">
          <translate>Get started</translate>
        </router-link>
      </div>

    </div>
  </section>
</template>

<script>
import { humanSize } from "@/filters"

export default {
  computed: {
    labels() {
      return {
        title: this.$gettext("Add and manage content")
      }
    },
    defaultQuota() {
      let quota =
        this.$store.state.instance.settings.users.upload_quota.value *
        1000 *
        1000
      return humanSize(quota)
    }
  }
}
</script>
