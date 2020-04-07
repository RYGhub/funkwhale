<template>
  <div class="channel-serie-card">
    <div class="two-images">
      <img @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-if="cover.original" v-lazy="$store.getters['instance/absoluteUrl'](cover.square_crop)">
      <img @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-else src="../../assets/audio/default-cover.png">
      <img @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-if="cover.original" v-lazy="$store.getters['instance/absoluteUrl'](cover.square_crop)">
      <img @click="$router.push({name: 'library.albums.detail', params: {id: serie.id}})" class="channel-image" v-else src="../../assets/audio/default-cover.png">
    </div>
    <div class="content">
      <strong>
        <router-link class="discrete ellipsis link" :title="serie.title" :to="{name: 'library.albums.detail', params: {id: serie.id}}">
          {{ serie.title|truncate(30) }}
        </router-link>
      </strong>
      <div class="description">
        <translate translate-context="Content/Channel/Paragraph"
          translate-plural="%{ count } episodes"
          :translate-n="serie.tracks.length"
          :translate-params="{count: serie.tracks.length}">
          %{ count } episode
        </translate>
      </div>
    </div>
    <div class="controls">
      <play-button :icon-only="true" :is-playable="true" :button-classes="['ui', 'circular', 'orange', 'icon', 'button']" :album="serie"></play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['serie'],
  components: {
    PlayButton,
  },
  computed: {
    imageUrl () {
      let url = '../../assets/audio/default-cover.png'
      let cover = this.cover
      if (cover && cover.original) {
        url = this.$store.getters['instance/absoluteUrl'](cover.medium_square_crop)
      } else {
        return null
      }
      return url
    },
    cover () {
      if (this.serie.cover) {
        return this.serie.cover
      }
    },
    duration () {
      let uploads = this.serie.uploads.filter((e) => {
        return e.duration
      })
      return uploads[0].duration
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.default-cover {
  background-image: url("../../assets/audio/default-cover.png") !important;
}
</style>
