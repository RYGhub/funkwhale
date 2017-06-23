<template>
  <table class="ui compact very basic fixed single line table">
    <thead>
      <tr>
        <th></th>
        <th></th>
        <th colspan="6">Title</th>
        <th colspan="6">Artist</th>
        <th colspan="6">Album</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="track in tracks">
        <td>
          <play-button class="basic icon" :discrete="true" :track="track"></play-button>
        </td>
        <td>
          <img class="ui mini image" v-if="track.album.cover" :src="backend.absoluteUrl(track.album.cover)">
          <img class="ui mini image" v-else src="../../..//assets/audio/default-cover.png">
        </td>
        <td colspan="6">
            <router-link class="track" :to="{name: 'browse.track', params: {id: track.id }}">
              {{ track.title }}
            </router-link>
        </td>
        <td colspan="6">
          <router-link class="artist discrete link" :to="{name: 'browse.artist', params: {id: track.artist.id }}">
            {{ track.artist.name }}
          </router-link>
        </td>
        <td colspan="6">
          <router-link class="album discrete link" :to="{name: 'browse.album', params: {id: track.album.id }}">
            {{ track.album.title }}
          </router-link>
        </td>
        <td><track-favorite-icon class="favorite-icon" :track="track"></track-favorite-icon></td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import backend from '@/audio/backend'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['tracks'],
  components: {
    TrackFavoriteIcon,
    PlayButton
  },
  data () {
    return {
      backend: backend
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

tr:not(:hover) .favorite-icon:not(.favorited) {
  display: none;
}
</style>
