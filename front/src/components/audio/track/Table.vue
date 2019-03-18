<template>
  <div class="table-wrapper">
    <table class="ui compact very basic unstackable table">
      <thead>
        <tr>
          <th></th>
          <th></th>
          <th colspan="6"><translate translate-context="Content/Track/*/Noun">Title</translate></th>
          <th colspan="4"><translate translate-context="*/*/*/Noun">Artist</translate></th>
          <th colspan="4"><translate translate-context="*/*/*">Album</translate></th>
          <th colspan="4"><translate translate-context="Content/*/*">Duration</translate></th>
          <th colspan="2"></th>
        </tr>
      </thead>
      <tbody>
        <track-row
          :playable="playable"
          :display-position="displayPosition"
          :track="track"
          :artist="artist"
          :key="index + '-' + track.id"
          v-for="(track, index) in tracks"></track-row>
      </tbody>
    </table>
  </div>
</template>

<script>
import backend from '@/audio/backend'

import TrackRow from '@/components/audio/track/Row'
import Modal from '@/components/semantic/Modal'

export default {
  props: {
    tracks: {type: Array, required: true},
    playable: {type: Boolean, required: false, default: false},
    artist: {type: Object, required: false},
    displayPosition: {type: Boolean, default: false}
  },
  components: {
    Modal,
    TrackRow
  },
  data () {
    return {
      backend: backend
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
tr:not(:hover) .favorite-icon:not(.favorited) {
  display: none;
}
pre {
  overflow-x: scroll;
}
</style>
