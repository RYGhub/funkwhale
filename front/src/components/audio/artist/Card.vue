<template>
  <div class="flat inline card">
    <div :class="['ui', 'image', 'with-overlay', {'default-cover': !cover.original}]" v-lazy:background-image="imageUrl">
      <play-button class="play-overlay" :icon-only="true" :is-playable="artist.is_playable" :button-classes="['ui', 'circular', 'large', 'orange', 'icon', 'button']" :artist="artist"></play-button>
    </div>
    <div class="content">
      <router-link :title="artist.name" :to="{name: 'library.artists.detail', params: {id: artist.id}}">
        {{ artist.name|truncate(30) }}
      </router-link>
      <div v-if="artist.albums.length > 0">
        <i class="small sound icon"></i>
        <translate translate-context="Content/Artist/Card" :translate-params="{count: artist.albums.length}" :translate-n="artist.albums.length" translate-plural="%{ count } albums">1 album</translate>
      </div>
      <div v-else-if="artist.tracks_count">
        <i class="small sound icon"></i>
        <translate translate-context="Content/Artist/Card" :translate-params="{count: artist.tracks_count}" :translate-n="artist.tracks_count" translate-plural="%{ count } tracks">1 track</translate>
      </div>
      <tags-list label-classes="tiny" :truncate-size="20" :limit="2" :show-more="false" :tags="artist.tags"></tags-list>

      <play-button
        class="play-button basic icon"
        :dropdown-only="true"
        :is-playable="artist.is_playable"
        :dropdown-icon-classes="['ellipsis', 'vertical', 'large', 'grey']"
        :artist="artist"></play-button>
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

.play-button {
  position: absolute;
  right: 0;
  bottom: 40%;
}

.with-overlay {
  background-size: cover !important;
  background-position: center !important;
  height: 8em;
  width: 8em;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}
.flat.card .with-overlay.image {
  border-radius: 50% !important;
  margin: 0 auto;
}
</style>
