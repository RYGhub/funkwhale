<template>
  <main v-title="labels.title">
    <section class="ui vertical stripe segment">
      <h2 class="ui header">
        <translate translate-context="Content/Artist/Title">Browsing artists</translate>
      </h2>
      <div :class="['ui', {'loading': isLoading}, 'form']">
        <div class="fields">
          <div class="field">
            <label>
              <translate translate-context="Content/Search/Input.Label/Noun">Search</translate>
            </label>
            <input type="text" name="search" v-model="query" :placeholder="labels.searchPlaceholder"/>
          </div>
          <div class="field">
            <label><translate translate-context="*/*/*/Noun">Tags</translate></label>
            <tags-selector v-model="tags"></tags-selector>
          </div>
          <div class="field">
            <label><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering</translate></label>
            <select class="ui dropdown" v-model="ordering">
              <option v-for="option in orderingOptions" :value="option[0]">
                {{ sharedLabels.filters[option[1]] }}
              </option>
            </select>
          </div>
          <div class="field">
            <label><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering direction</translate></label>
            <select class="ui dropdown" v-model="orderingDirection">
              <option value="+"><translate translate-context="Content/Search/Dropdown">Ascending</translate></option>
              <option value="-"><translate translate-context="Content/Search/Dropdown">Descending</translate></option>
            </select>
          </div>
          <div class="field">
            <label><translate translate-context="Content/Search/Dropdown.Label/Noun">Results per page</translate></label>
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
        item-selector=".card"
        percent-position="true"
        stagger="0">
        <div v-if="result.results.length > 0" class="ui cards">
          <artist-card
            v-masonry-tile
            v-for="artist in result.results"
            :key="artist.id"
            :artist="artist"></artist-card>
        </div>
      </div>
      <div class="ui center aligned basic segment">
        <pagination
          v-if="result && result.count > paginateBy"
          @page-changed="selectPage"
          :current="page"
          :paginate-by="paginateBy"
          :total="result.count"
          ></pagination>
      </div>
    </section>
  </main>
</template>

<script>
import qs from 'qs'
import axios from "axios"
import _ from "@/lodash"
import $ from "jquery"

import logger from "@/logging"

import OrderingMixin from "@/components/mixins/Ordering"
import PaginationMixin from "@/components/mixins/Pagination"
import TranslationsMixin from "@/components/mixins/Translations"
import ArtistCard from "@/components/audio/artist/Card"
import Pagination from "@/components/Pagination"
import TagsSelector from '@/components/library/TagsSelector'

const FETCH_URL = "artists/"

export default {
  mixins: [OrderingMixin, PaginationMixin, TranslationsMixin],
  props: {
    defaultQuery: { type: String, required: false, default: "" },
    defaultTags: { type: Array, required: false, default: () => { return [] } },
  },
  components: {
    ArtistCard,
    Pagination,
    TagsSelector,
  },
  data() {
    let defaultOrdering = this.getOrderingFromString(
      this.defaultOrdering || "-creation_date"
    )
    return {
      isLoading: true,
      result: null,
      page: parseInt(this.defaultPage),
      query: this.defaultQuery,
      tags: this.defaultTags.filter((t) => { return t.length > 0 }) || [],
      paginateBy: parseInt(this.defaultPaginateBy || 12),
      orderingDirection: defaultOrdering.direction || "+",
      ordering: defaultOrdering.field,
      orderingOptions: [["creation_date", "creation_date"], ["name", "name"]]
    }
  },
  created() {
    this.fetchData()
  },
  mounted() {
    $(".ui.dropdown").dropdown()
  },
  computed: {
    labels() {
      let searchPlaceholder = this.$pgettext('Content/Search/Input.Placeholder', "Enter artist name…")
      let title = this.$pgettext('*/*/*/Noun', "Artists")
      return {
        searchPlaceholder,
        title
      }
    }
  },
  methods: {
    updateQueryString: _.debounce(function() {
      this.$router.replace({
        query: {
          query: this.query,
          page: this.page,
          tag: this.tags,
          paginateBy: this.paginateBy,
          ordering: this.getOrderingAsString()
        }
      })
    }, 500),
    fetchData: _.debounce(function() {
      var self = this
      this.isLoading = true
      let url = FETCH_URL
      let params = {
        page: this.page,
        page_size: this.paginateBy,
        name__icontains: this.query,
        ordering: this.getOrderingAsString(),
        playable: "true",
        tag: this.tags,
      }
      logger.default.debug("Fetching artists")
      axios.get(
        url,
        {
          params: params,
          paramsSerializer: function(params) {
            return qs.stringify(params, { indices: false })
          }
        }
      ).then(response => {
        self.result = response.data
        self.isLoading = false
      })
    }, 500),
    selectPage: function(page) {
      this.page = page
    }
  },
  watch: {
    page() {
      this.updateQueryString()
      this.fetchData()
    },
    paginateBy() {
      this.updateQueryString()
      this.fetchData()
    },
    ordering() {
      this.updateQueryString()
      this.fetchData()
    },
    orderingDirection() {
      this.updateQueryString()
      this.fetchData()
    },
    query() {
      this.updateQueryString()
      this.fetchData()
    },
    tags() {
      this.updateQueryString()
      this.fetchData()
    },
    "$store.state.moderation.lastUpdate": function () {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
