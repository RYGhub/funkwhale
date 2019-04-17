<template>
  <div v-if="object">
    <div class="ui small text container" v-if="contentFilter">
      <div class="ui hidden divider"></div>
      <div class="ui message">
        <p>
          <translate translate-context="Content/Artist/Paragraph">You are currently hiding content related to this artist.</translate>
        </p>
        <router-link class="right floated" :to="{name: 'settings'}">
          <translate translate-context="Content/Moderation/Link">Review my filters</translate>
        </router-link>
        <button @click="$store.dispatch('moderation/deleteContentFilter', contentFilter.uuid)" class="ui basic tiny button">
          <translate translate-context="Content/Moderation/Button.Label">Remove filter</translate>
        </button>
      </div>
    </div>
    <section v-if="isLoadingAlbums" class="ui vertical stripe segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </section>
    <section v-else-if="albums && albums.length > 0" class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/Artist/Title">Albums by this artist</translate>
      </h2>
      <div class="ui cards" >
        <album-card :mode="'rich'" :album="album" :key="album.id" v-for="album in albums"></album-card>
      </div>
    </section>
    <section v-if="tracks.length > 0" class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/Artist/Title">Tracks by this artist</translate>
      </h2>
      <track-table :display-position="true" :tracks="tracks"></track-table>
    </section>
    <section class="ui vertical stripe segment">
      <h2>
        <translate translate-context="Content/*/Title/Noun">User libraries</translate>
      </h2>
      <library-widget @loaded="$emit('libraries-loaded', $event)" :url="'artists/' + object.id + '/libraries/'">
        <translate translate-context="Content/Artist/Paragraph" slot="subtitle">This artist is present in the following libraries:</translate>
      </library-widget>
    </section>
  </div>
</template>

<script>
import _ from "@/lodash"
import axios from "axios"
import logger from "@/logging"
import backend from "@/audio/backend"
import AlbumCard from "@/components/audio/album/Card"
import TrackTable from "@/components/audio/track/Table"
import LibraryWidget from "@/components/federation/LibraryWidget"

export default {
  props: ["object", "tracks", "albums", "isLoadingAlbums"],
  components: {
    AlbumCard,
    TrackTable,
    LibraryWidget,
  },
  computed: {
    contentFilter () {
      let self = this
      return this.$store.getters['moderation/artistFilters']().filter((e) => {
        return e.target.id === this.object.id
      })[0]
    }
  },
  watch: {
    id() {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
