<template>

</template>

<script>
import logger from '@/logging'
import config from '@/config'
import Vue from 'vue'
import router from '@/router'

export default {
  props: {
    metadata: {type: Object, required: true},
    defaultEnabled: {type: Boolean, default: true},
    backends: {type: Array},
    defaultBackendId: {type: String}
  },
  data () {
    return {
      currentBackendId: this.defaultBackendId,
      isImporting: false,
      enabled: this.defaultEnabled
    }
  },
  methods: {
    getMusicbrainzUrl (type, id) {
      return 'https://musicbrainz.org/' + type + '/' + id
    },
    launchImport () {
      let self = this
      this.isImporting = true
      let url = config.API_URL + 'submit/' + self.importType + '/'
      let payload = self.importData
      let resource = Vue.resource(url)
      resource.save({}, payload).then((response) => {
        logger.default.info('launched import for', self.type, self.metadata.id)
        self.isImporting = false
        router.push({
          name: 'library.import.batches.detail',
          params: {
            id: response.data.id
          }
        })
      }, (response) => {
        logger.default.error('error while launching import for', self.type, self.metadata.id)
        self.isImporting = false
      })
    }
  },
  computed: {
    importType () {
      return this.type
    },
    currentBackend () {
      let self = this
      return this.backends.filter(b => {
        return b.id === self.currentBackendId
      })[0]
    }
  },
  watch: {
    isImporting (newValue) {
      this.$emit('import-state-changed', newValue)
    },
    importData: {
      handler (newValue) {
        this.$emit('import-data-changed', newValue)
      },
      deep: true
    },
    enabled (newValue) {
      this.$emit('enabled', this.importData, newValue)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
