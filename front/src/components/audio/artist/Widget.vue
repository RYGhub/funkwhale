<template>
  <div class="wrapper">
    <h3 class="ui header">
      <slot name="title"></slot>
      <span class="ui tiny circular label">{{ count }}</span>
    </h3>
    <button v-if="controls" :disabled="!previousPage" @click="fetchData(previousPage)" :class="['ui', {disabled: !previousPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle left', 'icon']"></i></button>
    <button v-if="controls" :disabled="!nextPage" @click="fetchData(nextPage)" :class="['ui', {disabled: !nextPage}, 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'angle right', 'icon']"></i></button>
    <button v-if="controls" @click="fetchData('artists/')" :class="['ui', 'circular', 'icon', 'basic', 'button']"><i :class="['ui', 'refresh', 'icon']"></i></button>
    <div class="ui hidden divider"></div>
    <div class="ui three cards">
      <div v-if="isLoading" class="ui inverted active dimmer">
        <div class="ui loader"></div>
      </div>
      <div class="flat inline card" v-for="object in objects" :key="object.id">
        <div :class="['ui', 'image', 'with-overlay', {'default-cover': !getCover(object).original}]" v-lazy:background-image="getImageUrl(object)">
          <play-button class="play-overlay" :icon-only="true" :is-playable="object.is_playable" :button-classes="['ui', 'circular', 'large', 'orange', 'icon', 'button']" :artist="object"></play-button>
        </div>
        <div class="content">
          <router-link :title="object.name" :to="{name: 'library.artists.detail', params: {id: object.id}}">
            {{ object.name|truncate(30) }}
          </router-link>
          <div>
            <i class="small sound icon"></i>
            <translate translate-context="Content/Artist/Card" :translate-params="{count: object.albums.length}" :translate-n="object.albums.length" translate-plural="%{ count } albums">1 album</translate>
          </div>
          <tags-list label-classes="tiny" :truncate-size="20" :limit="2" :show-more="false" :tags="object.tags"></tags-list>

          <play-button
            class="play-button basic icon"
            :dropdown-only="true"
            :is-playable="object.is_playable"
            :dropdown-icon-classes="['ellipsis', 'vertical', 'large', 'grey']"
            :artist="object"></play-button>
        </div>
      </div>
    </div>
    <div v-if="!isLoading && objects.length === 0">No results matching your query.</div>
  </div>
</template>

<script>
import _ from '@/lodash'
import axios from 'axios'
import PlayButton from '@/components/audio/PlayButton'
import TagsList from "@/components/tags/List"

export default {
  props: {
    filters: {type: Object, required: true},
    controls: {type: Boolean, default: true},
  },
  components: {
    PlayButton,
    TagsList
  },
  data () {
    return {
      objects: [],
      limit: 12,
      count: 0,
      isLoading: false,
      errors: null,
      previousPage: null,
      nextPage: null
    }
  },
  created () {
    this.fetchData('artists/')
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
      params.offset = this.offset
      axios.get(url, {params: params}).then((response) => {
        self.previousPage = response.data.previous
        self.nextPage = response.data.next
        self.isLoading = false
        self.objects = response.data.results
        self.count = response.data.count
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
    },
    getImageUrl (object) {
      let url = '../../../assets/audio/default-cover.png'
      let cover = this.getCover(object)
      if (cover.original) {
        url = this.$store.getters['instance/absoluteUrl'](cover.medium_square_crop)
      } else {
        return null
      }
      return url
    },
    getCover (object) {
      return object.albums.map((a) => {
        return a.cover
      }).filter((c) => {
        return !!c
      })[0] || {}
    }
  },
  watch: {
    offset () {
      this.fetchData()
    },
    "$store.state.moderation.lastUpdate": function () {
      this.fetchData('objects/')
    }
  }
}
</script>
<style scoped lang="scss">
@import "../../../style/vendor/media";

.default-cover {
  background-image: url("../../../assets/audio/default-cover.png") !important;
}

.wrapper {
  width: 100%;
}
.ui.cards {
  justify-content: flex-start;
}
.play-button {
  position: absolute;
  right: 0;
  bottom: 0;
}

.ui.three.cards .card {
  width: 100%;
}
@include media(">tablet") {
  .ui.three.cards .card {
    width: 25em;
  }
}
.with-overlay {
  background-size: cover !important;
  background-position: center !important;
  height: 8em;
  width: 8em;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}
.flat.card .with-overlay.image {
  border-radius: 50% !important;
  margin: 0 auto;
}
</style>
<style>
.ui.cards .ui.button {
  margin-right: 0px;
}
</style>
