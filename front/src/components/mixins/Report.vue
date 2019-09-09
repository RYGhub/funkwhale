<script>
export default {
  methods: {
    getReportableObjs ({track, album, artist, playlist, account}) {
      let reportableObjs = []
      if (account) {
        let accountLabel = this.$pgettext('*/Moderation/*/Verb', "Report @%{ username }…")
        reportableObjs.push({
          label: this.$gettextInterpolate(accountLabel, {username: account.preferred_username}),
          target: {
            type: 'account',
            full_username: account.full_username,
            label: account.full_username,
            typeLabel: this.$pgettext("*/*/*", 'Account'),
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
            label: track.title,
            typeLabel: this.$pgettext("*/*/*", 'Track'),
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
            typeLabel: this.$pgettext("*/*/*", 'Artist'),
          }
        })
      }
      if (this.playlist) {
        reportableObjs.push({
          label: this.$pgettext('*/Moderation/*/Verb', "Report this playlist…"),
          target: {
            type: 'playlist',
            id: this.playlist.id,
            label: this.playlist.name,
            typeLabel: this.$pgettext("*/*/*", 'Playlist'),
          }
        })
      }
      return reportableObjs
    },
  }
}
</script>
