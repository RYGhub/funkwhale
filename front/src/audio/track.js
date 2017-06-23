import backend from './backend'

export default {
  getCover (track) {
    return backend.absoluteUrl(track.album.cover)
  }
}
