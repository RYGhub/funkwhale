<template>
  <div class="card app-card">
    <div
      @click="$router.push({name: 'library.albums.detail', params: {id: album.id}})"
      :class="['ui', 'head-image', 'image', {'default-cover': !album.cover.original}]" v-lazy:background-image="imageUrl">
      <play-button :icon-only="true" :is-playable="album.is_playable" :button-classes="['ui', 'circular', 'large', 'orange', 'icon', 'button']" :album="album"></play-button>
    </div>
    <div class="content">
      <strong>
        <router-link class="discrete link" :title="album.title" :to="{name: 'library.albums.detail', params: {id: album.id}}">
          {{ album.title }}
        </router-link>
      </strong>
      <div class="description">
        <span>
          <router-link :title="album.artist.name" class="discrete link" :to="{name: 'library.artists.detail', params: {id: album.artist.id}}">
            {{ album.artist.name }}
          </router-link>
        </span>
      </div>
    </div>
    <div class="extra content">
      <translate translate-context="*/*/*" :translate-params="{count: album.tracks.length}" :translate-n="album.tracks.length" translate-plural="%{ count } tracks">%{ count } track</translate>
      <play-button class="right floated basic icon" :dropdown-only="true" :is-playable="album.is_playable" :dropdown-icon-classes="['ellipsis', 'horizontal', 'large', 'grey']" :album="album"></play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    album: {type: Object},
  },
  components: {
    PlayButton
  },
  computed: {
    imageUrl () {
      let url = '../../../assets/audio/default-cover.png'

      if (this.album.cover.original) {
        url = this.$store.getters['instance/absoluteUrl'](this.album.cover.medium_square_crop)
      } else {
        return null
      }
      return url
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

.default-cover {
  background-image: url("../../../assets/audio/default-cover.png") !important;
}

.card.app-card > .head-image > .icon {
  margin: 0.5em;

}
</style>
