 <template>
  <button @click="$store.dispatch('favorites/set', {id: track.id, value: !isFavorite})" v-if="button" :class="['ui', 'pink', {'inverted': isFavorite}, {'favorited': isFavorite}, 'button']">
    <i class="heart icon"></i>
    <template v-if="isFavorite">
      In favorites
    </template>
    <template v-else>
      Add to favorites
    </template>
  </button>
  <i v-else @click="$store.dispatch('favorites/set', {id: track.id, value: !isFavorite})" :class="['favorite-icon', 'heart', {'pink': isFavorite}, {'favorited': isFavorite}, 'link', 'icon']" :title="title"></i>
</template>

<script>
import {mapState} from 'vuex'

export default {
  props: {
    track: {type: Object},
    button: {type: Boolean, default: false}
  },
  computed: {
    ...mapState({
      favorites: state => {
        return state.favorites.tracks
      }
    }),
    title () {
      if (this.isFavorite) {
        return 'Remove from favorites'
      } else {
        return 'Add to favorites'
      }
    },
    isFavorite () {
      return this.$store.getters['favorites/isFavorite'](this.track.id)
    }
  }

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
