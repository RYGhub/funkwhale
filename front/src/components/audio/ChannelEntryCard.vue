<template>
  <div class="channel-entry-card">
    <img @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})" class="channel-image image" v-if="cover && cover.original" v-lazy="$store.getters['instance/absoluteUrl'](cover.square_crop)">
    <img @click="$router.push({name: 'library.tracks.detail', params: {id: entry.id}})" class="channel-image image" v-else src="../../assets/audio/default-cover.png">
    <div class="content">
      <strong>
        <router-link class="discrete ellipsis link" :title="entry.title" :to="{name: 'library.tracks.detail', params: {id: entry.id}}">
          {{ entry.title|truncate(30) }}
        </router-link>
      </strong>
      <div class="description">
        <human-date :date="entry.creation_date"></human-date><template v-if="duration"> ·
        <human-duration :duration="duration"></human-duration></template>
      </div>
    </div>
    <div class="controls">
      <play-button :icon-only="true" :is-playable="true" :button-classes="['ui', 'circular', 'orange', 'icon', 'button']" :track="entry"></play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['entry'],
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
      if (this.entry.cover) {
        return this.entry.cover
      }
      if (this.entry.album && this.entry.album.cover) {
        return this.entry.album.cover
      }
    },
    duration () {
      let uploads = this.entry.uploads.filter((e) => {
        return e.duration
      })
      if (uploads.length > 0) {
        return uploads[0].duration
      }
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
