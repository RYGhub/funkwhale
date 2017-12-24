<template>
  <div>
    <div class="ui vertical stripe segment">
      <div v-if="isLoading" :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      <button
        class="ui left floated labeled icon button"
        @click="fetchData(previousLink)"
        :disabled="!previousLink"><i class="left arrow icon"></i> Previous</button>
      <button
        class="ui right floated right labeled icon button"
        @click="fetchData(nextLink)"
        :disabled="!nextLink">Next <i class="right arrow icon"></i></button>
      <div class="ui hidden clearing divider"></div>
      <div class="ui hidden clearing divider"></div>
      <table v-if="results.length > 0" class="ui table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Launch date</th>
            <th>Jobs</th>
            <th>Status</th>
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
                :class="['ui', {'yellow': result.status === 'pending'}, {'green': result.status === 'finished'}, 'label']">{{ result.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  </div>
</template>

<script>
import logger from '@/logging'
import config from '@/config'

const BATCHES_URL = config.API_URL + 'import-batches/'

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
      this.$http.get(url, {}).then((response) => {
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
