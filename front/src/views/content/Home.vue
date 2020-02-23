<template>
  <section class="ui vertical aligned stripe segment" v-title="labels.title">
    <div class="ui text container">
      <h1>{{ labels.title }}</h1>
      <p>
        <strong><translate translate-context="Content/Library/Paragraph" :translate-params="{quota: defaultQuota}">This instance offers up to %{quota} of storage space for every user.</translate></strong>
      </p>
      <div class="ui segment">
        <h2>
          <i class="feed icon"></i>&nbsp;
          <translate translate-context="Content/Library/Title/Verb">Publish your work in a channel</translate>
        </h2>
        <p>
          <translate translate-context="Content/Library/Paragraph">If you are a musician or a podcaster, channels are designed for you!</translate>
          <translate translate-context="Content/Library/Paragraph">Share your work publicly and get subscribers on Funkwhale, the Fediverse or any podcasting application.</translate>
        </p>
        <router-link :to="{name: 'profile.overview', params: {username: $store.state.auth.username}, hash: '#channels'}" class="ui primary button">
          <translate translate-context="Content/Library/Button.Label/Verb">Get started</translate>
        </router-link>
      </div>
      <div class="ui segment">
        <h2>
          <i class="cloud icon"></i>&nbsp;
          <translate translate-context="Content/Library/Title/Verb">Upload third-party content in a library</translate>
        </h2>
        <p><translate translate-context="Content/Library/Paragraph">Upload your personal music library to Funkwhale to enjoy it from anywhere and share it with friends and family.</translate></p>
        <router-link :to="{name: 'content.libraries.index'}" class="ui primary button">
          <translate translate-context="Content/Library/Button.Label/Verb">Get started</translate>
        </router-link>
      </div>
      <div class="ui segment">
        <h2>
          <i class="download icon"></i>&nbsp;
          <translate translate-context="Content/Library/Title/Verb">Follow remote libraries</translate>
        </h2>
        <p><translate translate-context="Content/Library/Paragraph">Follow libraries from other users to get access to new music. Public libraries can be followed immediately, while following a private library requires approval from its owner.</translate></p>
        <router-link :to="{name: 'content.remote.index'}" class="ui primary button">
          <translate translate-context="Content/Library/Button.Label/Verb">Get started</translate>
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
        title: this.$pgettext('Content/Library/Title/Verb', "Add and manage content")
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
