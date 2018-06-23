<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="'Album'">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="album">
      <div :class="['ui', 'head', {'with-background': album.cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="album.title">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted sound yellow icon"></i>
            <div class="content">
              {{ album.title }}
              <i18next tag="div" class="sub header" path="Album containing {%0%} tracks, by {%1%}">
                {{ album.tracks.length }}
                <router-link :to="{name: 'library.artists.detail', params: {id: album.artist.id }}">
                  {{ album.artist.name }}
                </router-link>
              </i18next>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          </button>
          <play-button class="orange" :tracks="album.tracks"><i18next path="Play all"/></play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            <i18next path="Search on Wikipedia"/>
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            <i18next path="View on MusicBrainz"/>
          </a>
        </div>
      </div>
      <div class="ui vertical stripe segment">
        <h2><i18next path="Tracks"/></h2>
        <track-table v-if="album" :display-position="true" :tracks="album.tracks"></track-table>
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
    wikipediaUrl () {
      return 'https://en.wikipedia.org/w/index.php?search=' + this.album.title + ' ' + this.album.artist.name
    },
    musicbrainzUrl () {
      return 'https://musicbrainz.org/release/' + this.album.mbid
    },
    headerStyle () {
      if (!this.album.cover) {
        return ''
      }
      return 'background-image: url(' + this.$store.getters['instance/absoluteUrl'](this.album.cover) + ')'
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
