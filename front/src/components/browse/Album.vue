<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="album">
      <div :class="['ui', 'head', {'with-background': album.cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted sound yellow icon"></i>
            <div class="content">
              {{ album.title }}
              <div class="sub header">
                Album containing {{ album.tracks.length }} tracks,
                by <router-link :to="{name: 'browse.artist', params: {id: album.artist.id }}">
                  {{ album.artist.name }}
                </router-link>
              </div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          </button>
          <play-button class="orange" :tracks="album.tracks">Play all</play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui button">
            <i class="wikipedia icon"></i>
            Search on wikipedia
          </a>
          <a :href="musicbrainzUrl" target="_blank" class="ui button">
            <i class="external icon"></i>
            View on MusicBrainz
          </a>
        </div>
      </div>
      <div class="ui vertical stripe segment">
        <h2>Tracks</h2>
        <track-table v-if="album" :tracks="album.tracks"></track-table>
      </div>
    </template>
  </div>
</template>

<script>

import logger from '@/logging'
import backend from '@/audio/backend'
import PlayButton from '@/components/audio/PlayButton'
import TrackTable from '@/components/audio/track/Table'
import config from '@/config'

const FETCH_URL = config.API_URL + 'albums/'

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
      this.$http.get(url).then((response) => {
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
      return 'background-image: url(' + backend.absoluteUrl(this.album.cover) + ')'
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
