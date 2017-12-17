 <template>
  <button @click="favoriteTracks.set(track.id, !isFavorite)" v-if="button" :class="['ui', 'pink', {'inverted': isFavorite}, {'favorited': isFavorite}, 'button']">
    <i class="heart icon"></i>
    <template v-if="isFavorite">
      In favorites
    </template>
    <template v-else>
      Add to favorites
    </template>
  </button>
  <i v-else @click="favoriteTracks.set(track.id, !isFavorite)" :class="['favorite-icon', 'heart', {'pink': isFavorite}, {'favorited': isFavorite}, 'link', 'icon']" :title="title"></i>
</template>

<script>
import favoriteTracks from '@/favorites/tracks'

export default {
  props: {
    track: {type: Object},
    button: {type: Boolean, default: false}
  },
  data () {
    return {
      favoriteTracks
    }
  },
  computed: {
    title () {
      if (this.isFavorite) {
        return 'Remove from favorites'
      } else {
        return 'Add to favorites'
      }
    },
    isFavorite () {
      return favoriteTracks.objects[this.track.id]
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
