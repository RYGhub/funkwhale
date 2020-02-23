<template>
  <section>
    <div>
      <h2 class="ui header">
        <translate translate-context="Content/Home/Title">Recently listened</translate>
      </h2>
      <track-widget :url="'history/listenings/'" :filters="{scope: `actor:${object.full_username}`, ordering: '-creation_date'}">
      </track-widget>
    </div>
    <div class="ui hidden divider"></div>
    <div>
      <h2 class="ui header">
        <translate translate-context="Content/Home/Title">Recently favorited</translate>
      </h2>
      <track-widget :url="'favorites/tracks/'" :filters="{scope: `actor:${object.full_username}`, ordering: '-creation_date'}"></track-widget>
    </div>
    <div class="ui hidden divider"></div>
    <div>
      <h2 class="ui header">
        <translate translate-context="*/*/*">Playlists</translate>
      </h2>
      <playlist-widget :url="'playlists/'" :filters="{scope: `actor:${object.full_username}`, playable: true, ordering: '-modification_date'}">
      </playlist-widget>
    </div>
  </section>
</template>

<script>
import TrackWidget from "@/components/audio/track/Widget"
import PlaylistWidget from "@/components/playlists/Widget"

export default {
  props: ['object'],
  components: {TrackWidget, PlaylistWidget},
}
</script>
