<template>
  <div v-title="'Import Batches'">
    <div class="ui vertical stripe segment">
      <div v-if="isLoading" :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      <button
        class="ui left floated labeled icon button"
        @click="fetchData(previousLink)"
        :disabled="!previousLink"><i class="left arrow icon"></i><i18next path="Previous"/></button>
      <button
        class="ui right floated right labeled icon button"
        @click="fetchData(nextLink)"
        :disabled="!nextLink"><i18next path="Next"/><i class="right arrow icon"></i></button>
      <div class="ui hidden clearing divider"></div>
      <div class="ui hidden clearing divider"></div>
      <table v-if="results.length > 0" class="ui unstackable table">
        <thead>
          <tr>
            <i18next tag="th" path="ID"/>
            <i18next tag="th" path="Launch date"/>
            <i18next tag="th" path="Jobs"/>
            <i18next tag="th" path="Status"/>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in results">
            <td>{{ result.id }}</th>
            <td>
              <router-link :to="{name: 'library.import.batches.detail', params: {id: result.id }}">
                {{ result.creation_date }}
              </router-link>
            </td>
            <td>{{ result.jobs.length }}</td>
            <td>
              <span
                :class="['ui', {'yellow': result.status === 'pending'}, {'red': result.status === 'errored'}, {'green': result.status === 'finished'}, 'label']">{{ result.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'

const BATCHES_URL = 'import-batches/'

export default {
  components: {},
  data () {
    return {
      results: [],
      isLoading: false,
      nextLink: null,
      previousLink: null
    }
  },
  created () {
    this.fetchData(BATCHES_URL)
  },
  methods: {
    fetchData (url) {
      var self = this
      this.isLoading = true
      logger.default.time('Loading import batches')
      axios.get(url, {}).then((response) => {
        self.results = response.data.results
        self.nextLink = response.data.next
        self.previousLink = response.data.previous
        logger.default.timeEnd('Loading import batches')
        self.isLoading = false
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
