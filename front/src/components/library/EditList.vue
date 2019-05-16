<template>
  <div class="wrapper">
    <h3 class="ui header">
      <slot name="title"></slot>
    </h3>
    <slot v-if="!isLoading && objects.length === 0" name="empty-state"></slot>
    <button v-if="nextPage || previousPage" :disabled="!previousPage" @click="fetchData(previousPage)" :class="['ui', {disabled: !previousPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle left', 'icon']"></i></button>
    <button v-if="nextPage || previousPage" :disabled="!nextPage" @click="fetchData(nextPage)" :class="['ui', {disabled: !nextPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle right', 'icon']"></i></button>
    <div class="ui hidden divider"></div>
    <div v-if="isLoading" class="ui inverted active dimmer">
      <div class="ui loader"></div>
    </div>
    <edit-card @updated="fetchData(url)" @deleted="fetchData(url)" v-for="obj in objects" :key="obj.uuid" :obj="obj" :current-state="currentState" />
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'

import EditCard from '@/components/library/EditCard'

export default {
  props: {
    url: {type: String, required: true},
    filters: {type: Object, required: false, default: () => {return {}}},
    currentState: {required: false},
  },
  components: {
    EditCard
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
  },
  watch: {
    filters: {
      handler () {
        this.fetchData(this.url)
      },
      deep: true
    }
  }
}
</script>
