<template>
  <div class="ui card">
    <div class="content">
        <div class="header">
          <router-link class="discrete link" :to="{name: 'library.artists.detail', params: {id: artist.id }}">
            {{ artist.name }}
          </router-link>
        </div>
        <div class="description">
          <table class="ui compact very basic fixed single line table">
            <tbody>
              <tr v-for="album in albums">
                <td>
                  <img class="ui mini image" v-if="album.cover" :src="backend.absoluteUrl(album.cover)">
                  <img class="ui mini image" v-else src="../../../assets/audio/default-cover.png">
                </td>
                <td colspan="4">
                  <router-link class="discrete link":to="{name: 'library.albums.detail', params: {id: album.id }}">
                    <strong>{{ album.title }}</strong>
                  </router-link><br />
                  {{ album.tracks.length }} tracks
                </td>
                <td>
                  <play-button class="right floated basic icon" :discrete="true" :tracks="album.tracks"></play-button>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="center aligned segment" v-if="artist.albums.length > initialAlbums">
            <em v-if="!showAllAlbums" @click="showAllAlbums = true" class="expand">Show {{ artist.albums.length - initialAlbums }} more albums</em>
            <em v-else @click="showAllAlbums = false" class="expand">Collapse</em>
          </div>
        </div>
    </div>
    <div class="extra content">
        <span>
          <i class="sound icon"></i>
          {{ artist.albums.length }} albums
        </span>
        <play-button class="mini basic orange right floated" :tracks="allTracks">Play all</play-button>
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
      initialAlbums: 3,
      showAllAlbums: false
    }
  },
  computed: {
    albums () {
      if (this.showAllAlbums) {
        return this.artist.albums
      }
      return this.artist.albums.slice(0, this.initialAlbums)
    },
    allTracks () {
      let tracks = []
      this.artist.albums.forEach(album => {
        album.tracks.forEach(track => {
          tracks.push(track)
        })
      })
      return tracks
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
