<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical center aligned stripe segment">
      <div :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
        <div class="ui text loader">
          <translate>Loading your favorites...</translate>
        </div>
      </div>
      <h2 v-if="results" class="ui center aligned icon header">
        <i class="circular inverted heart pink icon"></i>
        <translate
          translate-plural="%{ count } favorites"
          :translate-n="$store.state.favorites.count"
          :translate-params="{count: $store.state.favorites.count}">
          1 favorite
        </translate>
      </h2>
      <radio-button type="favorites"></radio-button>
    </div>
    <div class="ui vertical stripe segment">
      <div :class="['ui', {'loading': isLoading}, 'form']">
        <div class="fields">
          <div class="field">
            <label><translate>Ordering</translate></label>
            <select class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ option[1] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label><translate>Ordering direction</translate></label>
            <select class="ui dropdown" v-model="orderingDirection">
              <option value="+"><translate>Ascending</translate></option>
              <option value="-"><translate>Descending</translate></option>
            </select>
          </div>
          <div class="field">
            <label><translate>Results per page</translate></label>
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
          v-if="results && results.count > paginateBy"
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
    let defaultOrdering = this.getOrderingFromString(this.defaultOrdering || '-creation_date')
    return {
      results: null,
      isLoading: false,
      nextLink: null,
      previousLink: null,
      page: parseInt(this.defaultPage),
      paginateBy: parseInt(this.defaultPaginateBy || 25),
      orderingDirection: defaultOrdering.direction || '+',
      ordering: defaultOrdering.field,
      orderingOptions: [
        ['creation_date', 'Creation date'],
        ['title', 'Track name'],
        ['album__title', 'Album name'],
        ['artist__name', 'Artist name']
      ]
    }
  },
  created () {
    this.fetchFavorites(FAVORITES_URL)
  },
  mounted () {
    $('.ui.dropdown').dropdown()
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Your Favorites')
      }
    }
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
    },
    paginateBy: function () {
      this.updateQueryString()
    },
    orderingDirection: function () {
      this.updateQueryString()
    },
    ordering: function () {
      this.updateQueryString()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
