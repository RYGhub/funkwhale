<template>
  <div>
    <slot></slot>
    <div class="ui hidden divider"></div>
    <div v-if="isLoading" class="ui inverted active dimmer">
      <div class="ui loader"></div>
    </div>
    <channel-serie-card v-for="serie in objects" :serie="serie" :key="serie.id" />
    <template v-if="nextPage">
      <div class="ui hidden divider"></div>
      <button v-if="nextPage" @click="fetchData(nextPage)" :class="['ui', 'basic', 'button']">
        <translate translate-context="*/*/Button,Label">Show more</translate>
      </button>
    </template>
    <template v-if="!isLoading && objects.length === 0">
      <div class="ui placeholder segment">
        <div class="ui icon header">
          <i class="compact disc icon"></i>
          No results matching your query
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import ChannelSerieCard from '@/components/audio/ChannelSerieCard'

export default {
  props: {
    filters: {type: Object, required: true},
    limit: {type: Number, default: 5},
  },
  components: {
    ChannelSerieCard
  },
  data () {
    return {
      objects: [],
      count: 0,
      isLoading: false,
      errors: null,
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
      params.include_channels = true
      axios.get(url, {params: params}).then((response) => {
        self.nextPage = response.data.next
        self.isLoading = false
        self.objects = self.objects.concat(response.data.results)
        self.count = response.data.count
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
  }
}
</script>
