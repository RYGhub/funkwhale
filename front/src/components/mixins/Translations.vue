<script>
export default {
  computed: {
    sharedLabels () {
      return {
        fields: {
          privacy_level: {
            label: this.$pgettext('Content/Settings/Dropdown.Label/Noun', 'Activity visibility'),
            help: this.$pgettext('Content/Settings/Dropdown.Help text', 'Determine the visibility level of your activity'),
            choices: {
              me: this.$pgettext('Content/Settings/Dropdown', 'Nobody except me'),
              instance: this.$pgettext('Content/Settings/Dropdown', 'Everyone on this instance'),
            }
          }
        },
        filters: {
          creation_date: this.$pgettext('Content/*/Dropdown/Noun', 'Creation date'),
          first_seen: this.$pgettext('Content/Moderation/Dropdown/Noun', 'First seen date'),
          last_seen: this.$pgettext('Content/Moderation/Dropdown/Noun', 'Last seen date'),
          modification_date: this.$pgettext('Content/Playlist/Dropdown/Noun', 'Modification date'),
          expiration_date: this.$pgettext('Content/Admin/Table.Label/Noun', 'Expiration date'),
          track_title: this.$pgettext('Content/*/Dropdown/Noun', 'Track name'),
          album_title: this.$pgettext('Content/*/Dropdown/Noun', 'Album name'),
          artist_name: this.$pgettext('Content/*/Dropdown/Noun', 'Artist name'),
          name: this.$pgettext('Content/Moderation/*/Noun', 'Name'),
          size: this.$pgettext('Content/Library/*/Noun, in MB', 'Size'),
          bitrate: this.$pgettext('Content/*/*', 'Bitrate'),
          duration: this.$pgettext('Content/*/*', 'Duration'),
          date_joined: this.$pgettext('Content/Profile/*/Noun', 'Sign-up date'),
          last_activity: this.$pgettext('Content/Profile/*/Noun', 'Last activity'),
          username: this.$pgettext('Content/Profile/*/Noun', 'Username'),
          domain: this.$pgettext('Content/Moderation/*/Noun', 'Domain'),
          users: this.$pgettext('Content/Moderation/*/Noun', 'Users'),
          received_messages: this.$pgettext('Content/Moderation/Dropdown/Noun', 'Received messages'),
          uploads: this.$pgettext('Content/Moderation/Table.Label/Noun', 'Uploads'),
          followers: this.$pgettext('Content/Federation/*/Noun', 'Followers'),
        }
      }
    }
  }
}
</script>
