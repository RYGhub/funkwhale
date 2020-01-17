<template>
  <div class="app-card card">
    <div
      @click="$router.push({name: 'library.artists.detail', params: {id: artist.id}})"
      :class="['ui', 'head-image', 'circular', 'image', {'default-cover': !cover.original}]" v-lazy:background-image="imageUrl">
      <play-button :icon-only="true" :is-playable="artist.is_playable" :button-classes="['ui', 'circular', 'large', 'orange', 'icon', 'button']" :artist="artist"></play-button>
    </div>
    <div class="content">
      <strong>
        <router-link class="discrete link" :title="artist.name" :to="{name: 'library.artists.detail', params: {id: artist.id}}">
          {{ artist.name|truncate(30) }}
        </router-link>
      </strong>

      <tags-list label-classes="tiny" :truncate-size="20" :limit="2" :show-more="false" :tags="artist.tags"></tags-list>
    </div>
    <div class="extra content">
      <translate translate-context="*/*/*" :translate-params="{count: artist.tracks_count}" :translate-n="artist.tracks_count" translate-plural="%{ count } tracks">%{ count } track</translate>
      <play-button class="right floated basic icon" :dropdown-only="true" :is-playable="artist.is_playable" :dropdown-icon-classes="['ellipsis', 'horizontal', 'large', 'grey']" :artist="artist"></play-button>
    </div>
  </div>
</template>

<script>
import backend from '@/audio/backend'
import PlayButton from '@/components/audio/PlayButton'
import TagsList from "@/components/tags/List"

export default {
  props: ['artist'],
  components: {
    PlayButton,
    TagsList
  },
  data () {
    return {
      backend: backend,
      initialAlbums: 30,
      showAllAlbums: true,
    }
  },
  computed: {
    imageUrl () {
      let url = '../../../assets/audio/default-cover.png'
      let cover = this.cover
      if (cover.original) {
        url = this.$store.getters['instance/absoluteUrl'](cover.medium_square_crop)
      } else {
        return null
      }
      return url
    },
    cover () {
      if (this.artist.cover) {
        return this.artist.cover
      }
      return this.artist.albums.map((a) => {
        return a.cover
      }).filter((c) => {
        return !!c
      })[0] || {}
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.default-cover {
  background-image: url("../../../assets/audio/default-cover.png") !important;
}
</style>
