<template>
  <button
    @click.stop="$store.commit('playlists/chooseTrack', track)"
    v-if="button"
    :class="['ui', 'icon', 'labeled', 'button']">
    <i class="list icon"></i>
    <translate translate-context="Sidebar/Player/Icon.Tooltip/Verb">Add to playlist…</translate>
  </button>
  <button
    v-else
    @click.stop="$store.commit('playlists/chooseTrack', track)"
    :class="['ui', 'basic', 'circular', 'icon', 'really', 'button']"
    :aria-label="labels.addToPlaylist"
    :title="labels.addToPlaylist">
    <i :class="['list', 'basic', 'icon']"></i>
  </button>
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
  },
  computed: {
    labels () {
      return {
        addToPlaylist: this.$pgettext('Sidebar/Player/Icon.Tooltip/Verb', 'Add to playlist…')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
