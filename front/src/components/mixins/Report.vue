<script>
export default {
  methods: {
    getReportableObjs ({track, album, artist, playlist, account, library, channel}) {
      let reportableObjs = []
      if (account) {
        let accountLabel = this.$pgettext('*/Moderation/*/Verb', "Report @%{ username }…")
        reportableObjs.push({
          label: this.$gettextInterpolate(accountLabel, {username: account.preferred_username}),
          target: {
            type: 'account',
            _obj: account,
            full_username: account.full_username,
            label: account.full_username,
            typeLabel: this.$pgettext("*/*/*/Noun", 'Account'),
          }
        })
        if (track) {
          album = track.album
          artist = track.artist
        }
      }
      if (track) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this track…"),
          target: {
            type: 'track',
            id: track.id,
            _obj: track,
            label: track.title,
            typeLabel: this.$pgettext("*/*/*/Noun", 'Track'),
          }
        })
        album = track.album
        artist = track.artist
      }
      if (album) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this album…"),
          target: {
            type: 'album',
            id: album.id,
            label: album.title,
            _obj: album,
            typeLabel: this.$pgettext("*/*/*", 'Album'),
          }
        })
        if (!artist) {
          artist = album.artist
        }
      }
      if (artist) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this artist…"),
          target: {
            type: 'artist',
            id: artist.id,
            label: artist.name,
            _obj: artist,
            typeLabel: this.$pgettext("*/*/*/Noun", 'Artist'),
          }
        })
      }
      if (playlist) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this playlist…"),
          target: {
            type: 'playlist',
            id: playlist.id,
            label: playlist.name,
            _obj: playlist,
            typeLabel: this.$pgettext("*/*/*", 'Playlist'),
          }
        })
      }
      if (library) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this library…"),
          target: {
            type: 'library',
            uuid: library.uuid,
            label: library.name,
            _obj: library,
            typeLabel: this.$pgettext("*/*/*/Noun", 'Library'),
          }
        })
      }
      return reportableObjs
    },
  }
}
</script>
