<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment" v-title="">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="album">
      <section :class="['ui', 'head', {'with-background': album.cover.original}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="album.title">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted sound yellow icon"></i>
            <div class="content">
              {{ album.title }}
              <div v-html="subtitle"></div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <play-button class="orange" :tracks="album.tracks">
            <translate translate-context="Content/*/Button.Label/Verb, Short">Play all</translate>
          </play-button>

          <a :href="wikipediaUrl" target="_blank" class="ui icon labeled button">
            <i class="wikipedia w icon"></i>
            <translate translate-context="Content/*/Button.Label/Verb">Search on Wikipedia</translate>
          </a>
          <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" class="ui icon labeled button">
            <i class="external icon"></i>
            <translate translate-context="Content/*/Button.Label/Verb">View on MusicBrainz</translate>
          </a>
          <template v-if="publicLibraries.length > 0">
            <button
              @click="showEmbedModal = !showEmbedModal"
              class="ui button icon labeled">
              <i class="code icon"></i>
              <translate translate-context="Content/*/Button.Label/Verb">Embed</translate>
            </button>
            <modal :show.sync="showEmbedModal">
              <div class="header">
                <translate translate-context="Popup/Album/Title/Verb">Embed this album on your website</translate>
              </div>
              <div class="content">
                <div class="description">
                  <embed-wizard type="album" :id="album.id" />

                </div>
              </div>
              <div class="actions">
                <div class="ui deny button">
                  <translate translate-context="Popup/*/Button.Label/Verb">Cancel</translate>
                </div>
              </div>
            </modal>
          </template>
        </div>
      </section>
      <template v-if="discs && discs.length > 1">
        <section v-for="(tracks, disc_number) in discs" class="ui vertical stripe segment">
          <translate
            tag="h2"
            class="left floated"
            :translate-params="{number: disc_number + 1}"
            translate-context="Content/Album/"
          >Volume %{ number }</translate>
          <play-button class="right floated orange" :tracks="tracks">
            <translate translate-context="Content/*/Button.Label/Verb, Short">Play all</translate>
          </play-button>
          <track-table :artist="album.artist" :display-position="true" :tracks="tracks"></track-table>
        </section>
      </template>
      <template v-else>
        <section class="ui vertical stripe segment">
          <h2>
            <translate translate-context="Content/*/Title/Name">Tracks</translate>
          </h2>
          <track-table v-if="album" :artist="album.artist" :display-position="true" :tracks="album.tracks"></track-table>
        </section>
      </template>
      <section class="ui vertical stripe segment">
        <h2>
          <translate translate-context="Content/*/Title/Name">User libraries</translate>
        </h2>
        <library-widget @loaded="libraries = $event" :url="'albums/' + id + '/libraries/'">
          <translate slot="subtitle" translate-context="Content/Album/Paragraph">This album is present in the following libraries:</translate>
        </library-widget>
      </section>
    </template>
  </main>
</template>

<script>
import axios from "axios"
import logger from "@/logging"
import backend from "@/audio/backend"
import PlayButton from "@/components/audio/PlayButton"
import TrackTable from "@/components/audio/track/Table"
import LibraryWidget from "@/components/federation/LibraryWidget"
import EmbedWizard from "@/components/audio/EmbedWizard"
import Modal from '@/components/semantic/Modal'

const FETCH_URL = "albums/"

function groupByDisc(acc, track) {
  var dn = track.disc_number - 1
  if (dn < 0) dn = 0
  if (acc[dn] == undefined) {
    acc.push([track])
  } else {
    acc[dn].push(track)
  }
  return acc
}

export default {
  props: ["id"],
  components: {
    PlayButton,
    TrackTable,
    LibraryWidget,
    EmbedWizard,
    Modal
  },
  data() {
    return {
      isLoading: true,
      album: null,
      discs: [],
      libraries: [],
      showEmbedModal: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      let url = FETCH_URL + this.id + "/"
      logger.default.debug('Fetching album "' + this.id + '"')
      axios.get(url).then(response => {
        self.album = backend.Album.clean(response.data)
        self.discs = self.album.tracks.reduce(groupByDisc, [])
        self.isLoading = false
      })
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('Head/Album/Title/Name', 'Album')
      }
    },
    publicLibraries () {
      return this.libraries.filter(l => {
        return l.privacy_level === 'everyone'
      })
    },
    wikipediaUrl() {
      return (
        "https://en.wikipedia.org/w/index.php?search=" +
        encodeURI(this.album.title + " " + this.album.artist.name)
      )
    },
    musicbrainzUrl() {
      if (this.album.mbid) {
        return "https://musicbrainz.org/release/" + this.album.mbid
      }
    },
    headerStyle() {
      if (!this.album.cover.original) {
        return ""
      }
      return (
        "background-image: url(" +
        this.$store.getters["instance/absoluteUrl"](this.album.cover.original) +
        ")"
      )
    },
    subtitle () {
      let route = this.$router.resolve({name: 'library.artists.detail', params: {id: this.album.artist.id }})
      let msg = this.$npgettext('Content/Album/Header.Title', 'Album containing %{ count } track, by <a class="internal" href="%{ artistUrl }">%{ artist }</a>', 'Album containing %{ count } tracks, by <a class="internal" href="%{ artistUrl }">%{ artist }</a>', this.album.tracks.length)
      return this.$gettextInterpolate(msg, {count: this.album.tracks.length, artist: this.album.artist.name, artistUrl: route.location.path})
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
<style scoped lang="scss">
</style>
