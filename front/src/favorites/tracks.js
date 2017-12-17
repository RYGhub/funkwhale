import config from '@/config'
import logger from '@/logging'
import Vue from 'vue'

const REMOVE_URL = config.API_URL + 'favorites/tracks/remove/'
const FAVORITES_URL = config.API_URL + 'favorites/tracks/'

export default {
  objects: {},
  count: 0,
  set (id, newValue) {
    let self = this
    Vue.set(self.objects, id, newValue)
    if (newValue) {
      Vue.set(self, 'count', self.count + 1)
      let resource = Vue.resource(FAVORITES_URL)
      resource.save({}, {'track': id}).then((response) => {
        logger.default.info('Successfully added track to favorites')
      }, (response) => {
        logger.default.info('Error while adding track to favorites')
        Vue.set(self.objects, id, !newValue)
        Vue.set(self, 'count', self.count - 1)
      })
    } else {
      Vue.set(self, 'count', self.count - 1)
      let resource = Vue.resource(REMOVE_URL)
      resource.delete({}, {'track': id}).then((response) => {
        logger.default.info('Successfully removed track from favorites')
      }, (response) => {
        logger.default.info('Error while removing track from favorites')
        Vue.set(self.objects, id, !newValue)
        Vue.set(self, 'count', self.count + 1)
      })
    }
  },
  toggle (id) {
    let isFavorite = this.objects[id]
    this.set(id, !isFavorite)
  },
  fetch (url) {
    // will fetch favorites by batches from API to have them locally
    var self = this
    url = url || FAVORITES_URL
    let resource = Vue.resource(url)
    resource.get().then((response) => {
      logger.default.info('Fetched a batch of ' + response.data.results.length + ' favorites')
      Vue.set(self, 'count', response.data.count)
      response.data.results.forEach(result => {
        Vue.set(self.objects, result.track, true)
      })
      if (response.data.next) {
        self.fetch(response.data.next)
      }
    })
  }

}
