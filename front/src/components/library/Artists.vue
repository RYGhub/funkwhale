<template>
  <div v-title="'Artists'">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">Browsing artists</h2>
      <div :class="['ui', {'loading': isLoading}, 'form']">
        <div class="fields">
          <div class="field">
            <label>Search</label>
            <input type="text" v-model="query" placeholder="Enter an artist name..."/>
          </div>
          <div class="field">
            <label>Ordering</label>
            <select class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ option[1] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label>Ordering direction</label>
            <select class="ui dropdown" v-model="orderingDirection">
              <option value="">Ascending</option>
              <option value="-">Descending</option>
            </select>
          </div>
          <div class="field">
            <label>Results per page</label>
            <select class="ui dropdown" v-model="paginateBy">
              <option :value="parseInt(12)">12</option>
              <option :value="parseInt(25)">25</option>
              <option :value="parseInt(50)">50</option>
            </select>
          </div>
        </div>
      </div>
      <div class="ui hidden divider"></div>
      <div
        v-if="result"
        v-masonry
        transition-duration="0"
        item-selector=".column"
        percent-position="true"
        stagger="0"
        class="ui stackable three column doubling grid">
        <div
          v-masonry-tile
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
import axios from 'axios'
import _ from 'lodash'
import $ from 'jquery'

import backend from '@/audio/backend'
import logger from '@/logging'

import OrderingMixin from '@/components/mixins/Ordering'
import PaginationMixin from '@/components/mixins/Pagination'
import ArtistCard from '@/components/audio/artist/Card'
import Pagination from '@/components/Pagination'

const FETCH_URL = 'artists/'

export default {
  mixins: [OrderingMixin, PaginationMixin],
  props: {
    defaultQuery: {type: String, required: false, default: ''}
  },
  components: {
    ArtistCard,
    Pagination
  },
  data () {
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || '-creation_date')
    return {
      isLoading: true,
      result: null,
      page: parseInt(this.defaultPage),
      query: this.defaultQuery,
      paginateBy: parseInt(this.defaultPaginateBy || 12),
      orderingDirection: defaultOrdering.direction,
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['creation_date', 'Creation date'],
        ['name', 'Name']
      ]
    }
  },
  created () {
    this.fetchData()
  },
  mounted () {
    $('.ui.dropdown').dropdown()
  },
  methods: {
    updateQueryString: _.debounce(function () {
      this.$router.replace({
        query: {
          query: this.query,
          page: this.page,
          paginateBy: this.paginateBy,
          ordering: this.getOrderingAsString()
        }
      })
    }, 500),
    fetchData: _.debounce(function () {
      var self = this
      this.isLoading = true
      let url = FETCH_URL
      let params = {
        page: this.page,
        page_size: this.paginateBy,
        name__icontains: this.query,
        ordering: this.getOrderingAsString(),
        listenable: 'true'
      }
      logger.default.debug('Fetching artists')
      axios.get(url, {params: params}).then((response) => {
        self.result = response.data
        self.result.results.map((artist) => {
          var albums = JSON.parse(JSON.stringify(artist.albums)).map((album) => {
            return backend.Album.clean(album)
          })
          artist.albums = albums
          return artist
        })
        self.isLoading = false
      })
    }, 500),
    selectPage: function (page) {
      this.page = page
    }
  },
  watch: {
    page () {
      this.updateQueryString()
      this.fetchData()
    },
    paginateBy () {
      this.updateQueryString()
      this.fetchData()
    },
    ordering () {
      this.updateQueryString()
      this.fetchData()
    },
    orderingDirection () {
      this.updateQueryString()
      this.fetchData()
    },
    query () {
      this.updateQueryString()
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
