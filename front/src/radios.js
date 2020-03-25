import axios from "axios"
import logger from '@/logging'

// import axios from 'axios'

const RADIOS = {
  // some radios are client side only, so we have to implement the populateQueue
  // method by hand
  account: {
    offset: 1,
    populateQueue({current, dispatch, playNow}) {
      let params = {scope: `actor:${current.objectId.fullUsername}`, ordering: '-creation_date', page_size: 1, page: this.offset}
      axios.get('history/listenings', {params}).then((response) => {
        let latest = response.data.results[0]
        if (!latest) {
          logger.default.error('No more tracks')
          dispatch('stop')
        }
        this.offset += 1
        let append = dispatch('queue/append', {track: latest.track}, {root: true})
        if (playNow) {
          append.then(() => {
            dispatch('queue/last', null, {root: true})
          })
        }
      }, (error) => {
        logger.default.error('Error while fetching listenings', error)
        dispatch('stop')
      })
    },
    stop () {
      this.offset = 1
    },
    handleListen (current, event, store) {
      // XXX: handle actors from other pods
      if (event.actor.local_id === current.objectId.username) {
        axios.get(`tracks/${event.object.local_id}`).then((response) => {
          if (response.data.uploads.length > 0) {
            store.dispatch('queue/append', {track: response.data, index: store.state.queue.currentIndex + 1})
            this.offset += 1
          }
        }, (error) => {
          logger.default.error('Cannot retrieve track info', error)
        })
      }
    }
  }
}
export function getClientOnlyRadio({type}) {
  return RADIOS[type]
}
