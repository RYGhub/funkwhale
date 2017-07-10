<template>
    <div class="ui card">
      <div class="content">
        <div class="right floated tiny ui image">
          <img v-if="album.cover" :src="backend.absoluteUrl(album.cover)">
          <img v-else src="../../../assets/audio/default-cover.png">
        </div>
        <div class="header">
          <router-link class="discrete link" :to="{name: 'library.album', params: {id: album.id }}">{{ album.title }}</router-link>
        </div>
        <div class="meta">
          By <router-link :to="{name: 'library.artist', params: {id: album.artist.id }}">
            {{ album.artist.name }}
          </router-link>
        </div>
        <div class="description" v-if="mode === 'rich'">
          <table class="ui very basic fixed single line compact table">
            <tbody>
              <tr v-for="track in tracks">
                <td>
                  <play-button class="basic icon" :track="track" :discrete="true"></play-button>
                </td>
                <td colspan="6">
                  <router-link class="track discrete link" :to="{name: 'library.track', params: {id: track.id }}">
                    <template v-if="track.position">
                      {{ track.position }}.
                    </template>
                    {{ track.title }}
                  </router-link>
                </td>
                <td>
                  <track-favorite-icon :track="track"></track-favorite-icon>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="center aligned segment" v-if="album.tracks.length > initialTracks">
            <em v-if="!showAllTracks" @click="showAllTracks = true" class="expand">Show {{ album.tracks.length - initialTracks }} more tracks</em>
            <em v-else @click="showAllTracks = false" class="expand">Collapse</em>
          </div>
        </div>
      </div>
      <div class="extra content">
        <play-button class="mini basic orange right floated" :tracks="album.tracks">Play all</play-button>
        <span>
          <i class="music icon"></i>
          {{ album.tracks.length }} tracks
        </span>
      </div>
    </div>
</template>

<script>
import queue from '@/audio/queue'
import backend from '@/audio/backend'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    album: {type: Object},
    mode: {type: String, default: 'rich'}
  },
  components: {
    TrackFavoriteIcon,
    PlayButton
  },
  data () {
    return {
      backend: backend,
      queue: queue,
      initialTracks: 4,
      showAllTracks: false
    }
  },
  computed: {
    tracks () {
      if (this.showAllTracks) {
        return this.album.tracks
      }
      return this.album.tracks.slice(0, this.initialTracks)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

tr {
  .favorite-icon:not(.favorited) {
    display: none;
  }
  &:hover .favorite-icon {
    display: inherit;
  }
}
.expand {
  cursor: pointer;
}
</style>
