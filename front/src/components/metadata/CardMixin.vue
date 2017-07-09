<template>

</template>

<script>
import logger from '@/logging'

import config from '@/config'
import Vue from 'vue'

export default {
  props: {
    mbId: {type: String, required: true}
  },
  created: function () {
    this.fetchData()
  },
  data: function () {
    return {
      isLoading: false,
      data: {}
    }
  },
  methods: {
    fetchData () {
      let self = this
      this.isLoading = true
      let url = config.API_URL + 'providers/musicbrainz/' + this.type + 's/' + this.mbId + '/'
      let resource = Vue.resource(url)
      resource.get({}).then((response) => {
        logger.default.info('successfully fetched', self.type, self.mbId)
        self.data = response.data[self.type]
        this.$emit('metadata-changed', self.data)
        self.isLoading = false
      }, (response) => {
        logger.default.error('error while fetching', self.type, self.mbId)
        self.isLoading = false
      })
    },
    getMusicbrainzUrl (type, id) {
      return 'https://musicbrainz.org/' + type + '/' + id
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
