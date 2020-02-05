<template>
  <section class="ui stackable grid">
    <div class="six wide column">
      <rendered-description
        @updated="$emit('updated', $event)"
        :content="object.summary"
        :field-name="'summary'"
        :update-url="`users/users/${$store.state.auth.username}/`"
        :can-update="$store.state.auth.authenticated && object.full_username === $store.state.auth.fullUsername"></rendered-description>

    </div>
    <div class="ten wide column">
      <h2 class="ui header">
        <translate translate-context="*/*/*">Channels</translate>
      </h2>
      <channels-widget :filters="{scope: `actor:${object.full_username}`}"></channels-widget>
      <h2 class="ui header">
        <translate translate-context="Content/Profile/Header">User Libraries</translate>
      </h2>
      <library-widget :url="`federation/actors/${object.full_username}/libraries/`">
        <translate translate-context="Content/Profile/Paragraph" slot="subtitle">This user shared the following libraries.</translate>
      </library-widget>
    </div>
  </section>
</template>

<script>
import LibraryWidget from "@/components/federation/LibraryWidget"
import ChannelsWidget from "@/components/audio/ChannelsWidget"

export default {
  props: ['object'],
  components: {ChannelsWidget, LibraryWidget},
}
</script>
