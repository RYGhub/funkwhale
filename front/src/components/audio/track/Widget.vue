<template>
  <div>
    <h3 class="ui header">
      <slot name="title"></slot>
    </h3>
    <i @click="fetchData(previousPage)" :disabled="!previousPage" :class="['ui', {disabled: !previousPage}, 'circular', 'large', 'angle up', 'icon']">
    </i>
    <i @click="fetchData(nextPage)" :disabled="!nextPage" :class="['ui', {disabled: !nextPage}, 'circular', 'large', 'angle down', 'icon']">
    </i>
    <div class="ui divided unstackable items">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <div class="item" v-for="object in objects" :key="object.id">
        <div class="ui tiny image">
          <img v-if="object.track.album.cover" v-lazy="$store.getters['instance/absoluteUrl'](object.track.album.cover)">
          <img v-else src="../../../assets/audio/default-cover.png">
          <play-button class="play-overlay" :icon-only="true" :button-classes="['ui', 'circular', 'tiny', 'orange', 'icon', 'button']" :track="object.track"></play-button>
        </div>
        <div class="middle aligned content">
          <div class="ui unstackable grid">
            <div class="thirteen wide stretched column">
              <div>
                <router-link :title="object.track.title" :to="{name: 'library.tracks.detail', params: {id: object.track.id}}">
                  {{ object.track.title|truncate(25) }}
                </router-link>
              </div>
              <div class="meta">
                <span>
                  <router-link :title="object.track.artist.name" class="discrete link" :to="{name: 'library.artists.detail', params: {id: object.track.artist.id}}">
                    {{ object.track.artist.name|truncate(25) }}
                  </router-link>
                </span>
              </div>
              <div class="extra">
                <span class="left floated">@{{ object.user.username }}</span>
                <span class="right floated"><human-date :date="object.creation_date" /></span>
              </div>
            </div>
            <div class="one wide stretched column">
              <play-button class="basic icon" :dropdown-only="true" :dropdown-icon-classes="['ellipsis', 'vertical', 'large', 'grey']" :track="object.track"></play-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: {
    filters: {type: Object, required: true},
    url: {type: String, required: true}
  },
  components: {
    PlayButton
  },
  data () {
    return {
      objects: [],
      limit: 5,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null
    }
  },
  created () {
    this.fetchData(this.url)
  },
  methods: {
    fetchData (url) {
      if (!url) {
        return
      }
      this.isLoading = true
      let self = this
      let params = _.clone(this.filters)
      params.page_size = this.limit
      params.offset = this.offset
      axios.get(url, {params: params}).then((response) => {
        self.previousPage = response.data.previous
        self.nextPage = response.data.next
        self.isLoading = false
        self.objects = response.data.results
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    updateOffset (increment) {
      if (increment) {
        this.offset += this.limit
      } else {
        this.offset = Math.max(this.offset - this.limit, 0)
      }
    }
  },
  watch: {
    offset () {
      this.fetchData()
    }
  }
}
</script>

<style scoped lang="scss">
@import '../../../style/vendor/media';

.play-overlay {
  position: absolute;
  top: 4em;
  left: 4em;
  @include media(">tablet") {
    top: 2.5em;
    left: 2.5em;
  }
}
</style>
