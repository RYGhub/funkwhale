<template>
  <tr>
    <td>
      <play-button class="basic icon" :discrete="true" :track="track"></play-button>
    </td>
    <td>
      <img class="ui mini image" v-if="track.album.cover" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover)">
      <img class="ui mini image" v-else src="../../../assets/audio/default-cover.png">
    </td>
    <td colspan="6">
      <router-link class="track" :to="{name: 'library.tracks.detail', params: {id: track.id }}">
        <template v-if="displayPosition && track.position">
          {{ track.position }}.
        </template>
        {{ track.title }}
      </router-link>
    </td>
    <td colspan="6">
      <router-link v-if="track.artist.id === albumArtist.id" class="artist discrete link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
        {{ track.artist.name }}
      </router-link>
      <template v-else>
        <router-link class="artist discrete link" :to="{name: 'library.artists.detail', params: {id: albumArtist.id }}">
          {{ albumArtist.name }}
        </router-link>
         /
         <router-link class="artist discrete link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
          {{ track.artist.name }}
        </router-link>
      </template>
    </td>
    <td colspan="6">
      <router-link class="album discrete link" :to="{name: 'library.albums.detail', params: {id: track.album.id }}">
        {{ track.album.title }}
      </router-link>
    </td>
    <td>
      <track-favorite-icon class="favorite-icon" :track="track"></track-favorite-icon>
      <track-playlist-icon
        v-if="$store.state.auth.authenticated"
        :track="track"></track-playlist-icon>
    </td>
  </tr>
</template>

<script>
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import TrackPlaylistIcon from '@/components/playlists/TrackPlaylistIcon'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    track: {type: Object, required: true},
    artist: {type: Object, required: false},
    displayPosition: {type: Boolean, default: false}
  },
  components: {
    TrackFavoriteIcon,
    TrackPlaylistIcon,
    PlayButton
  },
  computed: {
    albumArtist () {
      if (this.artist) {
        return this.artist
      } else {
        return this.track.album.artist
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

tr:not(:hover) {
  .favorite-icon:not(.favorited), .playlist-icon {
    display: none;
  }
}
</style>
