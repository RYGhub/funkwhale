<template>
  <button
    @click="$store.commit('playlists/chooseTrack', track)"
    v-if="button"
    :class="['ui', 'button']">
    <i class="list icon"></i>
    <translate>Add to playlist...</translate>
  </button>
  <i
    v-else
    @click="$store.commit('playlists/chooseTrack', track)"
    :class="['playlist-icon', 'list', 'link', 'icon']"
    :title="$gettext('Add to playlist...')">
  </i>
</template>

<script>

export default {
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
