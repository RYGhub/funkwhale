<template>
  <div v-if="object">
    <template v-if="discs && discs.length > 1">
      <section v-for="(tracks, disc_number) in discs" class="ui vertical stripe segment">
        <translate
          tag="h2"
          class="left floated"
          :translate-params="{number: disc_number + 1}"
          translate-context="Content/Album/"
        >Volume %{ number }</translate>
        <play-button class="right floated orange" :tracks="tracks">
          <translate translate-context="Content/Queue/Button.Label/Short, Verb">Play all</translate>
        </play-button>
        <track-table :artist="object.artist" :display-position="true" :tracks="tracks"></track-table>
      </section>
    </template>
    <template v-else>
      <section class="ui vertical stripe segment">
        <h2>
          <translate translate-context="*/*/*/Noun">Tracks</translate>
        </h2>
        <track-table v-if="object" :artist="object.artist" :display-position="true" :tracks="object.tracks"></track-table>
      </section>
    </template>
    <section class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/*/Title/Noun">User libraries</translate>
      </h2>
      <library-widget @loaded="$emit('libraries-loaded', $event)" :url="'albums/' + object.id + '/libraries/'">
        <translate slot="subtitle" translate-context="Content/Album/Paragraph">This album is present in the following libraries:</translate>
      </library-widget>
    </section>
  </div>
</template>

<script>

import time from "@/utils/time"
import axios from "axios"
import url from "@/utils/url"
import logger from "@/logging"
import LibraryWidget from "@/components/federation/LibraryWidget"
import TrackTable from "@/components/audio/track/Table"

export default {
  props: ["object", "libraries", "discs"],
  components: {
    LibraryWidget,
    TrackTable
  },
  data() {
    return {
      time,
      id: this.object.id,
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
</style>
