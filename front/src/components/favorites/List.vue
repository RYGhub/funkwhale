<template>
  <div class="main pusher" v-title="'Your Favorites'">
    <div class="ui vertical center aligned stripe segment">
      <div :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
        <div class="ui text loader"><i18next path="Loading your favorites..."/></div>
      </div>
      <h2 v-if="results" class="ui center aligned icon header">
        <i class="circular inverted heart pink icon"></i>
        <i18next path="{%0%} favorites">
          {{ $store.state.favorites.count }}
        </i18next>
      </h2>
      <radio-button type="favorites"></radio-button>
    </div>
    <div class="ui vertical stripe segment">
      <div :class="['ui', {'loading': isLoading}, 'form']">
        <div class="fields">
          <div class="field">
            <i18next tag="label" path="Ordering"/>
            <select class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ option[1] }}
              </option>
            </select>
          </div>
          <div class="field">
            <i18next tag="label" path="Ordering direction"/>
            <select class="ui dropdown" v-model="orderingDirection">
              <option value=""><i18next path="Ascending"/></option>
              <option value="-"><i18next path="Descending"/></option>
            </select>
          </div>
          <div class="field">
            <i18next tag="label" path="Results per page"/>
            <select class="ui dropdown" v-model="paginateBy">
              <option :value="parseInt(12)">12</option>
              <option :value="parseInt(25)">25</option>
              <option :value="parseInt(50)">50</option>
            </select>
          </div>
        </div>
      </div>

      <track-table v-if="results" :tracks="results.results"></track-table>
      <div class="ui center aligned basic segment">
        <pagination
          v-if="results && results.count > 0"
          @page-changed="selectPage"
          :current="page"
          :paginate-by="paginateBy"
          :total="results.count"
          ></pagination>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import $ from 'jquery'
import logger from '@/logging'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'
import Pagination from '@/components/Pagination'
import OrderingMixin from '@/components/mixins/Ordering'
import PaginationMixin from '@/components/mixins/Pagination'
const FAVORITES_URL = 'tracks/'

export default {
  mixins: [OrderingMixin, PaginationMixin],
  components: {
    TrackTable,
    RadioButton,
    Pagination
  },
  data () {
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || 'artist__name')
    return {
      results: null,
      isLoading: false,
      nextLink: null,
      previousLink: null,
      page: parseInt(this.defaultPage),
      paginateBy: parseInt(this.defaultPaginateBy || 25),
      orderingDirection: defaultOrdering.direction,
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['title', this.$t('Track name')],
        ['album__title', this.$t('Album name')],
        ['artist__name', this.$t('Artist name')]
      ]
    }
  },
  created () {
    this.fetchFavorites(FAVORITES_URL)
  },
  mounted () {
    $('.ui.dropdown').dropdown()
  },
  methods: {
    updateQueryString: function () {
      this.$router.replace({
        query: {
          page: this.page,
          paginateBy: this.paginateBy,
          ordering: this.getOrderingAsString()
        }
      })
    },
    fetchFavorites (url) {
      var self = this
      this.isLoading = true
      let params = {
        favorites: 'true',
        page: this.page,
        page_size: this.paginateBy,
        ordering: this.getOrderingAsString()
      }
      logger.default.time('Loading user favorites')
      axios.get(url, {params: params}).then((response) => {
        self.results = response.data
        self.nextLink = response.data.next
        self.previousLink = response.data.previous
        self.results.results.forEach((track) => {
          self.$store.commit('favorites/track', {id: track.id, value: true})
        })
        logger.default.timeEnd('Loading user favorites')
        self.isLoading = false
      })
    },
    selectPage: function (page) {
      this.page = page
    }
  },
  watch: {
    page: function () {
      this.updateQueryString()
      this.fetchFavorites(FAVORITES_URL)
    },
    paginateBy: function () {
      this.updateQueryString()
      this.fetchFavorites(FAVORITES_URL)
    },
    orderingDirection: function () {
      this.updateQueryString()
      this.fetchFavorites(FAVORITES_URL)
    },
    ordering: function () {
      this.updateQueryString()
      this.fetchFavorites(FAVORITES_URL)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
