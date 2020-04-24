<template>
  <div>
    <slot></slot>
    <div class="ui hidden divider"></div>
    <div class="ui app-cards cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <channel-card v-for="object in objects" :object="object" :key="object.uuid" />
    </div>
    <template v-if="nextPage">
      <div class="ui hidden divider"></div>
      <button v-if="nextPage" @click="fetchData(nextPage)" :class="['ui', 'basic', 'button']">
        <translate translate-context="*/*/Button,Label">Show more</translate>
      </button>
    </template>
    <template v-if="!isLoading && objects.length === 0">
      <empty-state @refresh="fetchData('channels/')" :refresh="true"></empty-state>
    </template>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import ChannelCard from '@/components/audio/ChannelCard'

export default {
  props: {
    filters: {type: Object, required: true},
    limit: {type: Number, default: 5},
  },
  components: {
    ChannelCard
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
    this.fetchData('channels/')
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
        self.$emit('fetched', response.data)
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
  }
}
</script>
