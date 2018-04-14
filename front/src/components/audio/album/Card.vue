<template>
    <div class="ui card">
      <div class="content">
        <div class="right floated tiny ui image">
          <img v-if="album.cover" v-lazy="backend.absoluteUrl(album.cover)">
          <img v-else src="../../../assets/audio/default-cover.png">
        </div>
        <div class="header">
          <router-link class="discrete link" :to="{name: 'library.albums.detail', params: {id: album.id }}">{{ album.title }} </router-link>
        </div>
        <div class="meta">
          <span>
            <i18next path="By {%0%}">
              <router-link tag="span" :to="{name: 'library.artists.detail', params: {id: album.artist.id }}">
              {{ album.artist.name }}</router-link>
            </i18next>
          </span><span class="time" v-if="album.release_date">– {{ album.release_date | year }}</span>
        </div>
        <div class="description" v-if="mode === 'rich'">
          <table class="ui very basic fixed single line compact unstackable table">
            <tbody>
              <tr v-for="track in tracks">
                <td class="play-cell">
                  <play-button class="basic icon" :track="track" :discrete="true"></play-button>
                </td>
                <td colspan="6">
                  <router-link class="track discrete link" :to="{name: 'library.tracks.detail', params: {id: track.id }}">
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
            <em v-if="!showAllTracks" @click="showAllTracks = true" class="expand">
              <i18next path="Show {%0%} more tracks">{{ album.tracks.length - initialTracks }}</i18next>
            </em>
            <em v-else @click="showAllTracks = false" class="expand">
              <i18next path="Collapse" />
            </em>
          </div>
        </div>
      </div>
      <div class="extra content">
        <play-button class="mini basic orange right floated" :tracks="album.tracks">
          <i18next path="Play all"/>
        </play-button>
        <span>
          <i class="music icon"></i>
          <i18next path="{%0%} tracks">
            {{ album.tracks.length }}
          </i18next>
        </span>
      </div>
    </div>
</template>

<script>
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
      initialTracks: 5,
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

table.fixed td.play-cell {
  overflow: auto;
}
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
