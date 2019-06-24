<template>
    <div class="ui card">
      <div class="content">
        <div class="right floated tiny ui image">
          <img v-if="album.cover.original" v-lazy="$store.getters['instance/absoluteUrl'](album.cover.square_crop)">
          <img v-else src="../../../assets/audio/default-cover.png">
        </div>
        <div class="header">
          <router-link class="discrete link" :to="{name: 'library.albums.detail', params: {id: album.id }}">{{ album.title }} </router-link>
        </div>
        <div class="meta">
          <span>
            <router-link :title="album.artist.name" tag="span" :to="{name: 'library.artists.detail', params: {id: album.artist.id }}">
              <span v-translate="{artist: album.artist.name}" translate-context="Content/Album/Card" :translate-params="{artist: album.artist.name}">By %{ artist }</span>
            </router-link>
          </span><span class="time" v-if="album.release_date">– {{ album.release_date | year }}</span>
        </div>
        <div class="description" v-if="mode === 'rich'">
          <table class="ui very basic fixed single line compact unstackable table">
            <tbody>
              <tr v-for="track in tracks">
                <td class="play-cell">
                  <play-button :class="['basic', {orange: isPlaying && track.id === currentTrack.id}, 'icon']" :discrete="true" :track="track"></play-button>
                </td>
                <td class="content-cell" colspan="5">
                  <track-favorite-icon :track="track"></track-favorite-icon>
                  <router-link :title="track.title" class="track discrete link" :to="{name: 'library.tracks.detail', params: {id: track.id }}">
                    <template v-if="track.position">
                      {{ track.position }}.
                    </template>
                    {{ track.title }}
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="center aligned segment" v-if="album.tracks.length > initialTracks">
            <em v-if="!showAllTracks" @click="showAllTracks = true" class="expand">
              <translate translate-context="Content/Album/Card.Link/Verb" :translate-params="{count: album.tracks.length - initialTracks}" :translate-n="album.tracks.length - initialTracks" translate-plural="Show %{ count } more tracks">Show %{ count } more track</translate>
            </em>
            <em v-else @click="showAllTracks = false" class="expand">
              <translate translate-context="Content/*/Card.Link/Verb">Collapse</translate>
            </em>
          </div>
        </div>
      </div>
      <div class="extra content">
        <play-button class="mini basic orange right floated" :tracks="tracksWithAlbum" :album="album">
          <translate translate-context="Content/Queue/Button.Label/Short, Verb">Play all</translate>
        </play-button>
        <span>
          <i class="music icon"></i>
          <translate translate-context="*/*/*" :translate-params="{count: album.tracks.length}" :translate-n="album.tracks.length" translate-plural="%{ count } tracks">%{ count } track</translate>
        </span>
      </div>
    </div>
</template>

<script>
import { mapGetters } from "vuex"
import backend from '@/audio/backend'
import TrackFavoriteIcon from '@/components/favorites/TrackFavoriteIcon'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    album: {type: Object},
    mode: {type: String, default: 'rich'},
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
    },
    ...mapGetters({
      currentTrack: "queue/currentTrack",
    }),
    isPlaying () {
      return this.$store.state.player.playing
    },
    tracksWithAlbum () {
      // needed to include album data (especially cover)
      // with tracks appended in queue (#795)
      let self = this
      return this.album.tracks.map(t => {
        return  {
          ...t,
          album: {
            ...self.album,
            tracks: []
          }
        }
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.content-cell {
  .link,
  .button {
    padding: 0.5em 0;
  }
  .link {
    margin-left: 0.5em;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
tr {
  .favorite-icon:not(.favorited) {
    visibility: hidden;
  }
  &:hover .favorite-icon {
    visibility: visible;
  }
  .favorite-icon {
    float: right;
  }
}
.expand {
  cursor: pointer;
}
</style>
