<template>
  <tr>
    <td>
      <play-button :class="['basic', {orange: isPlaying && track.id === currentTrack.id}, 'icon']" :discrete="true" :is-playable="playable" :track="track"></play-button>
    </td>
    <td>
      <img class="ui mini image" v-if="track.album.cover.original" v-lazy="$store.getters['instance/absoluteUrl'](track.album.cover.small_square_crop)">
      <img class="ui mini image" v-else src="../../../assets/audio/default-cover.png">
    </td>
    <td colspan="6">
      <router-link class="track" :title="track.title" :to="{name: 'library.tracks.detail', params: {id: track.id }}">
        <template v-if="displayPosition && track.position">
          {{ track.position }}.
        </template>
        {{ track.title }}
      </router-link>
    </td>
    <td colspan="4">
      <router-link v-if="track.artist.id === albumArtist.id" :title="track.artist.name" class="artist discrete link" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
        {{ track.artist.name }}
      </router-link>
      <template v-else>
        <router-link class="artist discrete link" :title="albumArtist.name" :to="{name: 'library.artists.detail', params: {id: albumArtist.id }}">
          {{ albumArtist.name }}
        </router-link>
         /
         <router-link class="artist discrete link" :title="track.artist.name" :to="{name: 'library.artists.detail', params: {id: track.artist.id }}">
          {{ track.artist.name }}
        </router-link>
      </template>
    </td>
    <td colspan="4">
      <router-link class="album discrete link" :title="track.album.title" :to="{name: 'library.albums.detail', params: {id: track.album.id }}">
        {{ track.album.title }}
      </router-link>
    </td>
    <td colspan="4" v-if="track.uploads && track.uploads.length > 0">
      {{ time.parse(track.uploads[0].duration) }}
    </td>
    <td colspan="4" v-else>
      <translate translate-context="*/*/*">N/A</translate>
    </td>
    <td colspan="2" class="align right">
      <track-favorite-icon class="favorite-icon" :track="track"></track-favorite-icon>
      <track-playlist-icon
        v-if="$store.state.auth.authenticated"
        :track="track"></track-playlist-icon>
    </td>
  </tr>
</template>

<script>
import { mapGetters } from "vuex"
import time from '@/utils/time'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import TrackPlaylistIcon from '@/components/playlists/TrackPlaylistIcon'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    track: {type: Object, required: true},
    artist: {type: Object, required: false},
    displayPosition: {type: Boolean, default: false},
    playable: {type: Boolean, required: false, default: false},
  },
  components: {
    TrackFavoriteIcon,
    TrackPlaylistIcon,
    PlayButton
  },
  data () {
    return {
      time
    }
  },
  computed: {
    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),
    isPlaying () {
      return this.$store.state.player.playing
    },
    albumArtist () {
      if (this.artist) {
        return this.artist
      } else {
        return this.track.album.artist
      }
    },
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
tr:not(:hover) {
  .favorite-icon:not(.favorited),
  .playlist-icon {
    visibility: hidden;
  }
}
</style>
