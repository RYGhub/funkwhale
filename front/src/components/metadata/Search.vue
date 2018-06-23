<template>
  <div>
    <div class="ui form">
      <div class="inline fields">
        <div v-for="type in types"  class="field">
          <div class="ui radio checkbox">
            <input type="radio" :value="type.value" v-model="currentType">
            <label >{{ type.label }}</label>
          </div>
        </div>
      </div>
    </div>
    <div class="ui fluid search">
      <div class="ui icon input">
        <input class="prompt" :placeholder="$t('Enter your search query...')" type="text">
        <i class="search icon"></i>
      </div>
      <div class="results"></div>
    </div>
  </div>
</template>

<script>
import jQuery from 'jquery'

export default {
  props: {
    mbType: {type: String, required: false},
    mbId: {type: String, required: false}
  },
  data: function () {
    return {
      currentType: this.mbType || 'artist',
      currentId: this.mbId || ''
    }
  },

  mounted: function () {
    jQuery(this.$el).find('.ui.checkbox').checkbox()
    this.setUpSearch()
  },
  methods: {

    setUpSearch () {
      var self = this
      jQuery(this.$el).search({
        minCharacters: 3,
        onSelect (result, response) {
          self.currentId = result.id
        },
        apiSettings: {
          beforeXHR: function (xhrObject, s) {
            xhrObject.setRequestHeader('Authorization', self.$store.getters['auth/header'])
            return xhrObject
          },
          onResponse: function (initialResponse) {
            let category = self.currentTypeObject.value
            let results = initialResponse[category + '-list'].map(r => {
              let description = []
              if (category === 'artist') {
                if (r.type) {
                  description.push(r.type)
                }
                if (r.area) {
                  description.push(r.area.name)
                } else if (r['begin-area']) {
                  description.push(r['begin-area'].name)
                }
                return {
                  title: r.name,
                  id: r.id,
                  description: description.join(' - ')
                }
              }
              if (category === 'release') {
                if (r['medium-track-count']) {
                  description.push(
                    r['medium-track-count'] + ' tracks'
                  )
                }
                if (r['artist-credit-phrase']) {
                  description.push(r['artist-credit-phrase'])
                }
                if (r['date']) {
                  description.push(r['date'])
                }
                return {
                  title: r.title,
                  id: r.id,
                  description: description.join(' - ')
                }
              }
              if (category === 'recording') {
                if (r['artist-credit-phrase']) {
                  description.push(r['artist-credit-phrase'])
                }
                return {
                  title: r.title,
                  id: r.id,
                  description: description.join(' - ')
                }
              }
            })
            return {results: results}
          },
          url: this.searchUrl
        }
      })
    }
  },
  computed: {
    currentTypeObject: function () {
      let self = this
      return this.types.filter(t => {
        return t.value === self.currentType
      })[0]
    },
    searchUrl: function () {
      return this.$store.getters['instance/absoluteUrl']('providers/musicbrainz/search/' + this.currentTypeObject.value + 's/?query={query}')
    },
    types: function () {
      return [
        {
          value: 'artist',
          label: this.$t('Artist')
        },
        {
          value: 'release',
          label: this.$t('Album')
        },
        {
          value: 'recording',
          label: this.$t('Track')
        }
      ]
    }
  },
  watch: {
    currentType (newValue) {
      this.setUpSearch()
      this.$emit('type-changed', newValue)
    },
    currentId (newValue) {
      this.$emit('id-changed', newValue)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
