<template>
  <div class="ui card">
    <div class="content">
        <div class="header">
          <router-link class="discrete link" :to="{name: 'library.artists.detail', params: {id: artist.id }}">
            {{ artist.name }}
          </router-link>
        </div>
        <div class="description">
          <table class="ui compact very basic fixed single line unstackable table">
            <tbody>
              <tr v-for="album in albums">
                <td>
                  <img class="ui mini image" v-if="album.cover.original" v-lazy="$store.getters['instance/absoluteUrl'](album.cover.small_square_crop)">
                  <img class="ui mini image" v-else src="../../../assets/audio/default-cover.png">
                </td>
                <td colspan="4">
                  <router-link class="discrete link" :to="{name: 'library.albums.detail', params: {id: album.id }}">
                    <strong>{{ album.title }}</strong>
                  </router-link><br />
                  {{ album.tracks_count }} tracks
                </td>
                <td>
                  <play-button class="right floated basic icon" :is-playable="album.is_playable" :discrete="true" :album="album"></play-button>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="center aligned segment" v-if="artist.albums.length > initialAlbums">
            <em v-if="!showAllAlbums" @click="showAllAlbums = true" class="expand">
              <translate :translate-context="'Content/Artist/Card.Link'" :translate-params="{count: artist.albums.length - initialAlbums}" :translate-n="artist.albums.length - initialAlbums" translate-plural="Show %{ count } more albums">Show 1 more album</translate>
            </em>
            <em v-else @click="showAllAlbums = false" class="expand">
              <translate :translate-context="'Content/Artist/Card.Link'">Collapse</translate>
            </em>
          </div>
        </div>
    </div>
    <div class="extra content">
        <span>
          <i class="sound icon"></i>
            <translate :translate-context="'Content/Artist/Card'" :translate-params="{count: artist.albums.length}" :translate-n="artist.albums.length" translate-plural="%{ count } albums">1 album</translate>
        </span>
        <play-button :is-playable="isPlayable" class="mini basic orange right floated" :artist="artist">
          <translate :translate-context="'Content/Queue/Button.Label/Short, Verb'">Play all</translate>
        </play-button>
      </div>
    </div>
</template>

<script>
import backend from '@/audio/backend'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['artist'],
  components: {
    PlayButton
  },
  data () {
    return {
      backend: backend,
      initialAlbums: 30,
      showAllAlbums: true
    }
  },
  computed: {
    albums () {
      if (this.showAllAlbums) {
        return this.artist.albums
      }
      return this.artist.albums.slice(0, this.initialAlbums)
    },
    isPlayable () {
      return this.artist.albums.filter((a) => {
        return a.is_playable
      }).length > 0
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
