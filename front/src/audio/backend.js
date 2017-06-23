import config from '@/config'

var Album = {
  clean (album) {
    // we manually rebind the album and artist to each child track
    album.tracks = album.tracks.map((track) => {
      track.artist = album.artist
      track.album = album
      return track
    })
    return album
  }
}
var Artist = {
  clean (artist) {
    // clean data as given by the API
    artist.albums = artist.albums.map((album) => {
      return Album.clean(album)
    })
    return artist
  }
}
export default {
  absoluteUrl (url) {
    if (url.startsWith('http')) {
      return url
    }
    if (url.startsWith('/')) {
      return config.BACKEND_URL + url.substr(1)
    } else {
      return config.BACKEND_URL + url
    }
  },
  Artist: Artist,
  Album: Album

}
