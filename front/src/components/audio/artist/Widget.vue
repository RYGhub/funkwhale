<template>
  <div class="wrapper">
    <h3 v-if="header" class="ui header">
      <slot name="title"></slot>
      <span class="ui tiny circular label">{{ count }}</span>
    </h3>
    <button v-if="controls" :disabled="!previousPage" @click="fetchData(previousPage)" :class="['ui', {disabled: !previousPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle left', 'icon']"></i></button>
    <button v-if="controls" :disabled="!nextPage" @click="fetchData(nextPage)" :class="['ui', {disabled: !nextPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle right', 'icon']"></i></button>
    <button v-if="controls" @click="fetchData('artists/')" :class="['ui', 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'refresh', 'icon']"></i></button>
    <div class="ui hidden divider"></div>
    <div class="ui five app-cards cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <artist-card :artist="artist" v-for="artist in objects" :key="artist.id"></artist-card>
    </div>
    <div v-if="!isLoading && objects.length === 0">No results matching your query.</div>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import ArtistCard from "@/components/audio/artist/Card"

export default {
  props: {
    filters: {type: Object, required: true},
    controls: {type: Boolean, default: true},
    header: {type: Boolean, default: true},
  },
  components: {
    ArtistCard,
  },
  data () {
    return {
      objects: [],
      limit: 12,
      count: 0,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null
    }
  },
  created () {
    this.fetchData('artists/')
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
      this.fetchData('objects/')
    }
  }
}
</script>
<style scoped lang="scss">
@import "../../../style/vendor/media";

.wrapper {
  width: 100%;
}
.ui.cards {
  justify-content: flex-start;
}

.ui.three.cards .card {
  width: 100%;
}
@include media(">tablet") {
  .ui.three.cards .card {
    width: 25em;
  }
}
</style>
<style>
.ui.cards .ui.button {
  margin-right: 0px;
}
</style>
