<template>
  <div>
    <h3 class="ui header">
      <slot name="title"></slot>
    </h3>
    <i @click="fetchData(previousPage)" :disabled="!previousPage" :class="['ui', {disabled: !previousPage}, 'circular', 'large', 'angle up', 'icon']">
    </i>
    <i @click="fetchData(nextPage)" :disabled="!nextPage" :class="['ui', {disabled: !nextPage}, 'circular', 'large', 'angle down', 'icon']">
    </i>
    <div v-if="isLoading" class="ui inverted active dimmer">
      <div class="ui loader"></div>
    </div>
    <playlist-card class="fluid" v-for="playlist in objects" :key="playlist.id" :playlist="playlist"></playlist-card>
  </div>
</template>

<script>
import _ from 'lodash'
import axios from 'axios'
import PlaylistCard from '@/components/playlists/Card'

export default {
  props: {
    filters: {type: Object, required: true},
    url: {type: String, required: true}
  },
  components: {
    PlaylistCard
  },
  data () {
    return {
      objects: [],
      limit: 3,
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
