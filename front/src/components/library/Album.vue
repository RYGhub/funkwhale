<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="album">
      <div :class="['ui', 'head', {'with-background': album.cover.original}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="album.title">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted sound yellow icon"></i>
            <div class="content">
              {{ album.title }}
              <translate
                tag="div"
                translate-plural="Album containing %{ count } tracks, by %{ artist }"
                :translate-n="album.tracks.length"
                :translate-params="{count: album.tracks.length, artist: album.artist.name}">
                Album containing %{ count } track, by %{ artist }
              </translate>
            </div>
            <div class="ui basic buttons">
              <router-link class="ui button" :to="{name: 'library.artists.detail', params: {id: album.artist.id }}">
                <translate>Artist page</translate>
              </router-link>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <play-button class="orange" :tracks="album.tracks">
            <translate>Play all</translate>
          </play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <translate>Search on Wikipedia</translate>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <translate>View on MusicBrainz</translate>
          </a>
        </div>
      </div>
      <div class="ui vertical stripe segment">
        <h2>
          <translate>Tracks</translate>
        </h2>
        <track-table v-if="album" :artist="album.artist" :display-position="true" :tracks="album.tracks"></track-table>
      </div>
    </template>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'
import backend from '@/audio/backend'
import PlayButton from '@/components/audio/PlayButton'
import TrackTable from '@/components/audio/track/Table'

const FETCH_URL = 'albums/'

export default {
  props: ['id'],
  components: {
    PlayButton,
    TrackTable
  },
  data () {
    return {
      isLoading: true,
      album: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      let url = FETCH_URL + this.id + '/'
      logger.default.debug('Fetching album "' + this.id + '"')
      axios.get(url).then((response) => {
        self.album = backend.Album.clean(response.data)
        self.isLoading = false
      })
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Album')
      }
    },
    wikipediaUrl () {
      return 'https://en.wikipedia.org/w/index.php?search=' + this.album.title + ' ' + this.album.artist.name
    },
    musicbrainzUrl () {
      return 'https://musicbrainz.org/release/' + this.album.mbid
    },
    headerStyle () {
      if (!this.album.cover.original) {
        return ''
      }
      return 'background-image: url(' + this.$store.getters['instance/absoluteUrl'](this.album.cover.original) + ')'
    }
  },
  watch: {
    id () {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
