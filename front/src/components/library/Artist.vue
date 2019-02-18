<template>
  <main v-title="labels.title">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="artist">
      <section :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="artist.name">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted users violet icon"></i>
            <div class="content">
              {{ artist.name }}
              <div class="sub header" v-if="albums">
                <translate :translate-context="'Content/Artist/Paragraph'"
                  tag="div"
                  translate-plural="%{ count } tracks in %{ albumsCount } albums"
                  :translate-n="totalTracks"
                  :translate-params="{count: totalTracks, albumsCount: totalAlbums}">
                  %{ count } track in %{ albumsCount } albums
                </translate>
              </div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <radio-button type="artist" :object-id="artist.id"></radio-button>
          <play-button :is-playable="isPlayable" class="orange" :artist="artist">
            <translate :translate-context="'Content/Artist/Button.Label/Verb'">Play all albums</translate>
          </play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui icon labeled button">
            <i class="wikipedia w icon"></i>
            <translate :translate-context="'Content/*/Button.Label/Verb'">Search on Wikipedia</translate>
          </a>
          <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <translate :translate-context="'Content/*/Button.Label/Verb'">View on MusicBrainz</translate>
          </a>
        </div>
      </section>
      <div class="ui small text container" v-if="contentFilter">
        <div class="ui hidden divider"></div>
        <div class="ui message">
          <p>
            <translate>You are currently hiding content related to this artist.</translate>
          </p>
          <router-link class="right floated" :to="{name: 'settings'}">
            <translate :translate-context="'Content/Moderation/Link'">Review my filters</translate>
          </router-link>
          <button @click="$store.dispatch('moderation/deleteContentFilter', contentFilter.uuid)" class="ui basic tiny button">
            <translate :translate-context="'Content/Moderation/Button.Label'">Remove filter</translate>
          </button>
        </div>
      </div>
      <section v-if="isLoadingAlbums" class="ui vertical stripe segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </section>
      <section v-else-if="albums && albums.length > 0" class="ui vertical stripe segment">
        <h2>
          <translate :translate-context="'Content/Artist/Title'">Albums by this artist</translate>
        </h2>
        <div class="ui cards" >
          <album-card :mode="'rich'" :album="album" :key="album.id" v-for="album in albums"></album-card>
        </div>
      </section>
      <section v-if="tracks.length > 0" class="ui vertical stripe segment">
        <h2>
          <translate :translate-context="'Content/Artist/Title'">Tracks by this artist</translate>
        </h2>
        <track-table :display-position="true" :tracks="tracks"></track-table>
      </section>
      <section class="ui vertical stripe segment">
        <h2>
          <translate :translate-context="'Content/Artist/Title'">User libraries</translate>
        </h2>
        <library-widget :url="'artists/' + id + '/libraries/'">
          <translate :translate-context="'Content/Artist/Paragraph'" slot="subtitle">This artist is present in the following libraries:</translate>
        </library-widget>
      </section>
    </template>
  </main>
</template>

<script>
import _ from "@/lodash"
import axios from "axios"
import logger from "@/logging"
import backend from "@/audio/backend"
import AlbumCard from "@/components/audio/album/Card"
import RadioButton from "@/components/radios/Button"
import PlayButton from "@/components/audio/PlayButton"
import TrackTable from "@/components/audio/track/Table"
import LibraryWidget from "@/components/federation/LibraryWidget"

export default {
  props: ["id"],
  components: {
    AlbumCard,
    RadioButton,
    PlayButton,
    TrackTable,
    LibraryWidget
  },
  data() {
    return {
      isLoading: true,
      isLoadingAlbums: true,
      artist: null,
      albums: null,
      totalTracks: 0,
      totalAlbums: 0,
      tracks: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      logger.default.debug('Fetching artist "' + this.id + '"')
      axios.get("tracks/", { params: { artist: this.id, hidden: '' } }).then(response => {
        self.tracks = response.data.results
        self.totalTracks = response.data.count
      })
      axios.get("artists/" + this.id + "/").then(response => {
        self.artist = response.data
        self.isLoading = false
        self.isLoadingAlbums = true
        axios
          .get("albums/", {
            params: { artist: self.id, ordering: "-release_date", hidden: '' }
          })
          .then(response => {
            self.totalAlbums = response.data.count
            let parsed = JSON.parse(JSON.stringify(response.data.results))
            self.albums = parsed.map(album => {
              return backend.Album.clean(album)
            })

            self.isLoadingAlbums = false
          })
      })
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('Head/Artist/Title', "Artist")
      }
    },
    isPlayable() {
      return (
        this.artist.albums.filter(a => {
          return a.is_playable
        }).length > 0
      )
    },
    wikipediaUrl() {
      return (
        "https://en.wikipedia.org/w/index.php?search=" +
        encodeURI(this.artist.name)
      )
    },
    musicbrainzUrl() {
      if (this.artist.mbid) {
        return "https://musicbrainz.org/artist/" + this.artist.mbid
      }
    },
    allTracks() {
      let tracks = []
      this.albums.forEach(album => {
        album.tracks.forEach(track => {
          tracks.push(track)
        })
      })
      return tracks
    },
    cover() {
      return this.artist.albums
        .filter(album => {
          return album.cover
        })
        .map(album => {
          return album.cover
        })[0]
    },
    headerStyle() {
      if (!this.cover || !this.cover.original) {
        return ""
      }
      return (
        "background-image: url(" +
        this.$store.getters["instance/absoluteUrl"](this.cover.original) +
        ")"
      )
    },
    contentFilter () {
      let self = this
      return this.$store.getters['moderation/artistFilters']().filter((e) => {
        return e.target.id === this.artist.id
      })[0]
    }
  },
  watch: {
    id() {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
