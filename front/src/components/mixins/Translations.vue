<script>
export default {
  computed: {
    sharedLabels () {
      return {
        filters: {
          creation_date: this.$gettext('Creation date'),
          accessed_date: this.$gettext('Accessed date'),
          modification_date: this.$gettext('Modification date'),
          imported_date: this.$gettext('Imported date'),
          expiration_date: this.$gettext('Expiration date'),
          track_title: this.$gettext('Track name'),
          album_title: this.$gettext('Album name'),
          artist_name: this.$gettext('Artist name'),
          name: this.$gettext('Name'),
          title: this.$gettext('Title'),
          size: this.$gettext('Size'),
          bitrate: this.$gettext('Bitrate'),
          duration: this.$gettext('Duration'),
          date_joined: this.$gettext('Sign-up date'),
          last_activity: this.$gettext('Last activity'),
          username: this.$gettext('Username'),
        }
      }
    }
  }
}
</script>
