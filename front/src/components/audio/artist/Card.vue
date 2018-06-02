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
                  <img class="ui mini image" v-if="album.cover" :src="backend.absoluteUrl(album.cover)">
                  <img class="ui mini image" v-else src="../../../assets/audio/default-cover.png">
                </td>
                <td colspan="4">
                  <router-link class="discrete link":to="{name: 'library.albums.detail', params: {id: album.id }}">
                    <strong>{{ album.title }}</strong>
                  </router-link><br />
                  {{ album.tracks_count }} tracks
                </td>
                <td>
                  <play-button class="right floated basic icon" :discrete="true" :album="album.id"></play-button>
                </td>
              </tr>
            </tbody>
          </table>
          <div class="center aligned segment" v-if="artist.albums.length > initialAlbums">
            <em v-if="!showAllAlbums" @click="showAllAlbums = true" class="expand">
              <i18next path="Show {%0%} more albums">
                {{ artist.albums.length - initialAlbums }}
              </i18next>
            </em>
            <em v-else @click="showAllAlbums = false" class="expand">
              <i18next path="Collapse"/>
            </em>
          </div>
        </div>
    </div>
    <div class="extra content">
        <span>
          <i class="sound icon"></i>
          <i18next path="{%0%} albums">
            {{ artist.albums.length }}
          </i18next>
        </span>
        <play-button class="mini basic orange right floated" :artist="artist.id">
          <i18next path="Play all"/>
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
