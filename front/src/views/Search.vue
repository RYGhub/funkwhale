<template>
  <main class="main pusher" v-title="labels.title">
    <section class="ui vertical stripe segment">
      <div class="ui small text container">
        <form :class="['ui', {loading: isLoading}, 'form']" @submit.stop.prevent="createFetch">
          <h2><translate translate-context="Content/Fetch/Title">Retrieve a remote object</translate></h2>
          <p>
            <translate translate-context="Content/Fetch/Paragraph">Use this form to retrieve an object hosted somewhere else in the fediverse.</translate>
          </p>
          <div v-if="errors.length > 0" class="ui negative message">
            <div class="header"><translate translate-context="Content/*/Error message.Title">Error while fetching object</translate></div>
            <ul class="list">
              <li v-for="error in errors">{{ error }}</li>
            </ul>
          </div>
          <div class="ui required field">
            <label for="object-id">
              {{ labels.fieldLabel }}
            </label>
            <input type="text" name="object-id" id="object-id" v-model="id" required>
          </div>
          <button type="submit" :class="['ui', 'primary', {loading: isLoading}, 'button']" :disabled="isLoading || !id || id.length === 0">
            <translate translate-context="Content/Search/Input.Label/Noun">Search</translate>
          </button>
        </form>
        <div v-if="!isLoading && fetch && fetch.status === 'finished'">
          <div class="ui hidden divider"></div>
          <h2><translate translate-context="Content/Fetch/Title/Noun">Result</translate></h2>
          <div class="ui hidden divider"></div>
          <div v-if="objComponent" class="ui app-cards cards">
            <component v-bind="objComponent.props" :is="objComponent.type"></component>
          </div>
          <div v-else class="ui warning message">
            <p><translate translate-context="Content/*/Error message.Title">This kind of object isn't supported yet</translate></p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import axios from 'axios'


import AlbumCard from '@/components/audio/album/Card'
import ArtistCard from '@/components/audio/artist/Card'
import LibraryCard from '@/views/content/remote/Card'
import ChannelEntryCard from '@/components/audio/ChannelEntryCard'

export default {
  props: {
    initialId: { type: String, required: false}
  },
  components: {
    ActorLink:  () => import(/* webpackChunkName: "common" */ "@/components/common/ActorLink"),
    ArtistCard,
    AlbumCard,
    LibraryCard,
    ChannelEntryCard,
  },
  data () {
    return {
      id: this.initialId,
      fetch: null,
      obj: null,
      isLoading: false,
      errors: [],
    }
  },
  created () {
    if (this.id) {
      this.createFetch()
    }
  },
  computed: {
    labels() {
      return {
        title: this.$pgettext('Head/Fetch/Title', "Search a remote object"),
        fieldLabel: this.$pgettext('Head/Fetch/Field.Placeholder', "URL or @username"),
      }
    },
    objInfo () {
      if (this.fetch && this.fetch.status === 'finished') {
        return this.fetch.object
      }
    },
    objComponent () {
      if (!this.obj) {
        return
      }
      switch (this.objInfo.type) {
        case "account":
          return {
            type: "actor-link",
            props: {actor: this.obj}
          }
        case "library":
          return {
            type: "library-card",
            props: {library: this.obj}
          }
        case "album":
          return {
            type: "album-card",
            props: {album: this.obj}
          }
        case "artist":
          return {
            type: "artist-card",
            props: {artist: this.obj}
          }
        case "upload":
          return {
            type: "channel-entry-card",
            props: {entry: this.obj.track}
          }

        default:
          return
      }
    }
  },
  methods: {
    createFetch () {
      if (!this.id) {
        return
      }
      this.$router.replace({name: "search", query: {id: this.id}})
      this.fetch = null
      let self = this
      self.errors = []
      self.isLoading = true
      let payload = {
        object: this.id
      }

      axios.post('federation/fetches/', payload).then((response) => {
        self.isLoading = false
        self.fetch = response.data
        if (self.fetch.status === 'errored' || self.fetch.status === 'skipped') {
          self.errors.push(
            self.$pgettext("Content/*/Error message.Title", "This object cannot be retrieved")
          )
        }
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    getObj (objInfo) {
      if (!this.id) {
        return
      }
      let self = this
      self.isLoading = true
      let url = null
      switch (objInfo.type) {
        case 'account':
          url = `federation/actors/${objInfo.full_username}/`
          break;
        case 'library':
          url = `libraries/${objInfo.uuid}/`
          break;
        case 'artist':
          url = `artists/${objInfo.id}/`
          break;
        case 'album':
          url = `albums/${objInfo.id}/`
          break;
        case 'upload':
          url = `uploads/${objInfo.uuid}/`
          break;

        default:
          break;
      }
      if (!url) {
        this.errors.push(
          self.$pgettext("Content/*/Error message.Title", "This kind of object isn't supported yet")
        )
        this.isLoading = false
        return
      }
      axios.get(url).then((response) => {
        self.obj = response.data
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  watch: {
    initialId (v) {
      this.id = v
      this.createFetch()
    },
    objInfo (v) {
      this.obj = null
      if (v) {
        this.getObj(v)
      }
    }
  }
}
</script>
