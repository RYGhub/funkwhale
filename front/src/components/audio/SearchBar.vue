<template>
  <div class="ui fluid category search">
    <slot></slot>
    <div class="ui icon input">
      <input class="prompt" placeholder="Search for artists, albums, tracks..." type="text">
      <i class="search icon"></i>
    </div>
    <div class="results"></div>
    <slot name="after"></slot>
  </div>
</template>

<script>
import jQuery from 'jquery'
import config from '@/config'
import router from '@/router'

const SEARCH_URL = config.API_URL + 'search?query={query}'

export default {
  mounted () {
    let self = this
    jQuery(this.$el).search({
      type: 'category',
      minCharacters: 3,
      onSelect (result, response) {
        router.push(result.routerUrl)
      },
      onSearchQuery (query) {
        self.$emit('search')
      },
      apiSettings: {
        beforeXHR: function (xhrObject) {
          xhrObject.setRequestHeader('Authorization', self.$store.getters['auth/header'])
          return xhrObject
        },
        onResponse: function (initialResponse) {
          var results = {}
          let categories = [
            {
              code: 'artists',
              route: 'library.artists.detail',
              name: 'Artist',
              getTitle (r) {
                return r.name
              },
              getDescription (r) {
                return ''
              }
            },
            {
              code: 'albums',
              route: 'library.albums.detail',
              name: 'Album',
              getTitle (r) {
                return r.title
              },
              getDescription (r) {
                return ''
              }
            },
            {
              code: 'tracks',
              route: 'library.tracks.detail',
              name: 'Track',
              getTitle (r) {
                return r.title
              },
              getDescription (r) {
                return ''
              }
            }
          ]
          categories.forEach(category => {
            results[category.code] = {
              name: category.name,
              results: []
            }
            initialResponse[category.code].forEach(result => {
              results[category.code].results.push({
                title: category.getTitle(result),
                id: result.id,
                routerUrl: {
                  name: category.route,
                  params: {
                    id: result.id
                  }
                },
                description: category.getDescription(result)
              })
            })
          })
          return {results: results}
        },
        url: SEARCH_URL
      }
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
