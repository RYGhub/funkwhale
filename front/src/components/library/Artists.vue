<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="result" class="ui vertical stripe segment">
      <h2 class="ui header">Browsing artists</h2>
      <div class="ui stackable three column grid">
        <div
          v-if="result.results.length > 0"
          v-for="artist in result.results"
          :key="artist.id"
          class="column">
          <artist-card class="fluid" :artist="artist"></artist-card>
        </div>
      </div>
      <div class="ui center aligned basic segment">
        <pagination
          v-if="result && result.results.length > 0"
          @page-changed="selectPage"
          :current="page"
          :paginate-by="paginateBy"
          :total="result.count"
          ></pagination>
      </div>
    </div>
  </div>
</template>

<script>

import config from '@/config'
import logger from '@/logging'
import ArtistCard from '@/components/audio/artist/Card'
import Pagination from '@/components/Pagination'

const FETCH_URL = config.API_URL + 'artists/'

export default {
  components: {
    ArtistCard,
    Pagination
  },
  data () {
    return {
      isLoading: true,
      result: null,
      page: 1,
      orderBy: 'name',
      paginateBy: 12
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      let url = FETCH_URL
      let params = {
        page: this.page,
        page_size: this.paginateBy,
        order_by: 'name'
      }
      logger.default.debug('Fetching artists')
      this.$http.get(url, {params: params}).then((response) => {
        self.result = response.data
        self.isLoading = false
      })
    },
    selectPage: function (page) {
      this.page = page
    }
  },
  watch: {
    page () {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
