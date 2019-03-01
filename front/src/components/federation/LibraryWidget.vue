<template>
  <div class="wrapper">
    <h3 class="ui header">
      <slot name="title"></slot>
    </h3>
    <p v-if="!isLoading && libraries.length > 0" class="ui subtitle"><slot name="subtitle"></slot></p>
    <p v-if="!isLoading && libraries.length === 0" class="ui subtitle"><translate :translate-context="'Content/Federation/Paragraph'">No matching library.</translate></p>
    <i @click="fetchData(previousPage)" :disabled="!previousPage" :class="['ui', {disabled: !previousPage}, 'circular', 'angle left', 'icon']">
    </i>
    <i @click="fetchData(nextPage)" :disabled="!nextPage" :class="['ui', {disabled: !nextPage}, 'circular', 'angle right', 'icon']">
    </i>
    <div class="ui hidden divider"></div>
    <div class="ui cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <library-card
        :display-scan="false"
        :display-follow="$store.state.auth.authenticated"
        :library="library"
        :display-copy-fid="true"
        v-for="library in libraries"
        :key="library.uuid"></library-card>
    </div>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import LibraryCard from '@/views/content/remote/Card'

export default {
  props: {
    url: {type: String, required: true}
  },
  components: {
    LibraryCard
  },
  data () {
    return {
      libraries: [],
      limit: 6,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.isLoading = true
      let self = this
      let params = _.clone({})
      params.page_size = this.limit
      params.offset = this.offset
      axios.get(this.url, {params: params}).then((response) => {
        self.previousPage = response.data.previous
        self.nextPage = response.data.next
        self.isLoading = false
        self.libraries = response.data.results
        self.$emit('loaded', self.libraries)
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
