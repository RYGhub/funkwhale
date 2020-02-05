<template>
  <div class="wrapper">
    <h3 class="ui header">
      <slot name="title"></slot>
      <span v-if="showCount" class="ui tiny circular label">{{ count }}</span>
    </h3>
    <slot></slot>
    <div class="ui hidden divider"></div>
    <div class="ui app-cards cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <album-card v-for="album in albums" :album="album" :key="album.id" />
    </div>
    <template v-if="!isLoading && albums.length === 0">
      <div class="ui placeholder segment">
        <div class="ui icon header">
          <i class="compact disc icon"></i>
          No results matching your query
        </div>
      </div>
    </template>
    <template v-if="nextPage">
      <div class="ui hidden divider"></div>
      <button v-if="nextPage" @click="fetchData(nextPage)" :class="['ui', 'basic', 'button']">
        <translate translate-context="*/*/Button,Label">Show more</translate>
      </button>
    </template>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import AlbumCard from '@/components/audio/album/Card'

export default {
  props: {
    filters: {type: Object, required: true},
    controls: {type: Boolean, default: true},
    showCount: {type: Boolean, default: false},
    limit: {type: Number, default: 12},
  },
  components: {
    AlbumCard
  },
  data () {
    return {
      albums: [],
      count: 0,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null
    }
  },
  created () {
    this.fetchData('albums/')
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
        self.albums = [...self.albums, ...response.data.results]
        self.count = response.data.count
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
    },
  },
  watch: {
    offset () {
      this.fetchData()
    },
    "$store.state.moderation.lastUpdate": function () {
      this.fetchData('albums/')
    }
  }
}
</script>
<style scoped lang="scss">


.wrapper {
  width: 100%;
}
.ui.cards {
  justify-content: flex-start;
}
</style>
<style>
.ui.cards .ui.button {
  margin-right: 0px;
}
</style>
