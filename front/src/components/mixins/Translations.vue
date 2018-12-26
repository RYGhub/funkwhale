<script>
export default {
  computed: {
    sharedLabels () {
      return {
        fields: {
          privacy_level: {
            label: this.$gettext('Activity visibility'),
            help: this.$gettext('Determine the visibility level of your activity'),
            choices: {
              me: this.$gettext('Nobody except me'),
              instance: this.$gettext('Everyone on this instance'),
            }
          }
        },
        filters: {
          creation_date: this.$gettext('Creation date'),
          first_seen: this.$gettext('First seen date'),
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
          users: this.$gettext('Users'),
          received_messages: this.$gettext('Received messages'),
        }
      }
    }
  }
}
</script>
