<template>
  <div class="ui stackable grid">
    <div class="three wide column">
      <h5 class="ui header">
        {{ metadata.position }}. {{ metadata.recording.title }}
        <div class="sub header">
          {{ time.parse(parseInt(metadata.length) / 1000) }}
        </div>
      </h5>
      <div class="ui toggle checkbox">
        <input type="checkbox" v-model="enabled" />
        <i18next tag="label" path="Import this track"/>
      </div>
    </div>
    <div class="three wide column" v-if="enabled">
      <form class="ui mini form" @submit.prevent="">
        <div class="field">
          <i18next tag="label" path="Source"/>
          <select v-model="currentBackendId">
            <option v-for="backend in backends" :value="backend.id">
              {{ backend.label }}
            </option>
          </select>
        </div>
      </form>
      <div class="ui hidden divider"></div>
      <template v-if="currentResult">
        <button @click="currentResultIndex -= 1" class="ui basic tiny icon button" :disabled="currentResultIndex === 0">
          <i class="left arrow icon"></i>
        </button>
        <i18next path="Result {%0%}/{%1%}">
          {{ currentResultIndex + 1 }}
          {{ results.length }}
        </i18next>
        <button @click="currentResultIndex += 1" class="ui basic tiny icon button" :disabled="currentResultIndex + 1 === results.length">
          <i class="right arrow icon"></i>
        </button>
      </template>
    </div>
    <div class="four wide column" v-if="enabled">
      <form class="ui mini form" @submit.prevent="">
        <div class="field">
          <i18next tag="label" path="Search query"/>
          <input type="text" v-model="query" />
          <i18next tag="label" path="Imported URL"/>
          <input type="text" v-model="importedUrl" />
        </div>
      </form>
    </div>
    <div class="six wide column" v-if="enabled">
      <div v-if="isLoading" class="ui vertical segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <div v-if="!isLoading && currentResult" class="ui items">
        <div class="item">
          <div class="ui small image">
            <img :src="currentResult.cover" />
          </div>
          <div class="content">
            <a
              :href="currentResult.url"
              target="_blank"
              class="description"
              v-html="$options.filters.highlight(currentResult.title, warnings)"></a>
            <div v-if="currentResult.channelTitle" class="meta">
              {{ currentResult.channelTitle}}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'
import time from '@/utils/time'
import logger from '@/logging'
import ImportMixin from './ImportMixin'

import $ from 'jquery'

Vue.filter('highlight', function (words, query) {
  query.forEach(w => {
    let re = new RegExp('(' + w + ')', 'gi')
    words = words.replace(re, '<span class=\'highlight\'>$1</span>')
  })
  return words
})

export default Vue.extend({
  mixins: [ImportMixin],
  props: {
    releaseMetadata: {type: Object, required: true}
  },
  data () {
    return {
      isLoading: false,
      results: [],
      currentResultIndex: 0,
      importedUrl: '',
      warnings: [
        'live',
        'tv',
        'full',
        'cover',
        'mix'
      ],
      customQuery: '',
      time
    }
  },
  created () {
    if (this.enabled) {
      this.search()
    }
  },
  mounted () {
    $('.ui.checkbox').checkbox()
  },
  methods: {
    search: function () {
      let self = this
      this.isLoading = true
      let url = 'providers/' + this.currentBackendId + '/search/'
      axios.get(url, {params: {query: this.query}}).then((response) => {
        logger.default.debug('searching', self.query, 'on', self.currentBackendId)
        self.results = response.data
        self.isLoading = false
      }, (response) => {
        logger.default.error('error while searching', self.query, 'on', self.currentBackendId)
        self.isLoading = false
      })
    }
  },
  computed: {
    type () {
      return 'track'
    },
    currentResult () {
      if (this.results) {
        return this.results[this.currentResultIndex]
      }
    },
    importData () {
      return {
        count: 1,
        mbid: this.metadata.recording.id,
        source: this.importedUrl
      }
    },
    query: {
      get: function () {
        if (this.customQuery.length > 0) {
          return this.customQuery
        }
        let queryMapping = [
          ['artist', this.releaseMetadata['artist-credit'][0]['artist']['name']],
          ['album', this.releaseMetadata['title']],
          ['title', this.metadata['recording']['title']]
        ]
        let query = this.customQueryTemplate
        queryMapping.forEach(e => {
          query = query.split('$' + e[0]).join(e[1])
        })
        return query
      },
      set: function (newValue) {
        this.customQuery = newValue
      }
    }
  },
  watch: {
    query () {
      this.search()
    },
    currentResult (newValue) {
      if (newValue) {
        this.importedUrl = newValue.url
      }
    },
    importedUrl (newValue) {
      this.$emit('url-changed', this.importData, this.importedUrl)
    },
    enabled (newValue) {
      if (newValue && this.results.length === 0) {
        this.search()
      }
    }
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.ui.card {
    width: 100% !important;
}
</style>
<style lang="scss">
.highlight {
  font-weight: bold !important;
  background-color: yellow !important;
}
</style>
