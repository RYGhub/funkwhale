<template>
  <button
    @click="showModal = true"
    v-if="button"
    :class="['ui', 'button']">
    <i class="list icon"></i>
    Add to playlist...
    <playlist-modal :track="track" :show.sync="showModal"></playlist-modal>
  </button>
  <i
    v-else
    @click="showModal = true"
    :class="['favorite-icon', 'list', 'link', 'icon']"
    title="Add to playlist...">
    <playlist-modal :track="track" :show.sync="showModal"></playlist-modal>
  </i>
</template>

<script>
import PlaylistModal from '@/components/playlists/PlaylistModal'

export default {
  components: {
    PlaylistModal
  },
  props: {
    track: {type: Object},
    button: {type: Boolean, default: false}
  },
  data () {
    return {
      showModal: false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
