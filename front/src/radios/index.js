import Vue from 'vue'
import config from '@/config'
import logger from '@/logging'
import queue from '@/audio/queue'

const CREATE_RADIO_URL = config.API_URL + 'radios/sessions/'
const GET_TRACK_URL = config.API_URL + 'radios/tracks/'

var radios = {
  types: {
    random: {
      name: 'Random',
      description: "Totally random picks, maybe you'll discover new things?"
    },
    favorites: {
      name: 'Favorites',
      description: 'Play your favorites tunes in a never-ending happiness loop.'
    },
    'less-listened': {
      name: 'Less listened',
      description: "Listen to tracks you usually don't. It's time to restore some balance."
    }
  },
  start (type, objectId) {
    this.current.type = type
    this.current.objectId = objectId
    this.running = true
    let resource = Vue.resource(CREATE_RADIO_URL)
    var self = this
    var params = {
      radio_type: type,
      related_object_id: objectId
    }
    resource.save({}, params).then((response) => {
      logger.default.info('Successfully started radio ', type)
      self.current.session = response.data.id
      queue.populateFromRadio()
    }, (response) => {
      logger.default.error('Error while starting radio', type)
    })
  },
  stop () {
    this.current.type = null
    this.current.objectId = null
    this.running = false
    this.session = null
  },
  fetch () {
    let resource = Vue.resource(GET_TRACK_URL)
    var self = this
    var params = {
      session: self.current.session
    }
    return resource.save({}, params)
  }
}

Vue.set(radios, 'running', false)
Vue.set(radios, 'current', {})
Vue.set(radios.current, 'objectId', null)
Vue.set(radios.current, 'type', null)
Vue.set(radios.current, 'session', null)

export default radios
