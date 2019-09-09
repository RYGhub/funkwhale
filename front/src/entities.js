function getTagsValueRepr (val) {
  if (!val) {
    return ''
  }
  return val.slice().sort().join('\n')
}

export default {
  getConfigs () {
    return {
      artist: {
        label: this.$pgettext('*/*/*', 'Artist'),
        icon: 'users',
        getDeleteUrl: (obj) => {
          return `manage/library/artists/${obj.id}/`
        },
        urls: {
          getDetail: (obj) => { return {name: 'library.artists.detail', params: {id: obj.id}}},
          getAdminDetail: (obj) => { return {name: 'manage.library.artists.detail', params: {id: obj.id}}},
        },
        moderatedFields: [
          {
            id: 'name',
            label: this.$pgettext('*/*/*/Noun', 'Name'),
            getValue: (obj) => { return obj.name }
          },
          {
            id: 'creation_date',
            label: this.$pgettext('*/*/*/Noun', 'Creation date'),
            getValue: (obj) => { return obj.creation_date }
          },
          {
            id: 'tags',
            type: 'tags',
            label: this.$pgettext('*/*/*/Noun', 'Tags'),
            getValue: (obj) => { return obj.tags },
            getValueRepr: getTagsValueRepr
          },
          {
            id: 'mbid',
            label: this.$pgettext('*/*/*/Noun', 'MusicBrainz ID'),
            getValue: (obj) => { return obj.mbid }
          },
        ]
      },
      album: {
        label: this.$pgettext('*/*/*', 'Album'),
        icon: 'play',
        getDeleteUrl: (obj) => {
          return `manage/library/albums/${obj.id}/`
        },
        urls: {
          getDetail: (obj) => { return {name: 'library.albums.detail', params: {id: obj.id}}},
          getAdminDetail: (obj) => { return {name: 'manage.library.albums.detail', params: {id: obj.id}}}
        },
        moderatedFields: [
          {
            id: 'title',
            label: this.$pgettext('*/*/*/Noun', 'Title'),
            getValue: (obj) => { return obj.title }
          },
          {
            id: 'creation_date',
            label: this.$pgettext('*/*/*/Noun', 'Creation date'),
            getValue: (obj) => { return obj.creation_date }
          },
          {
            id: 'release_date',
            label: this.$pgettext('Content/*/*/Noun', 'Release date'),
            getValue: (obj) => { return obj.release_date }
          },
          {
            id: 'tags',
            type: 'tags',
            required: true,
            label: this.$pgettext('*/*/*/Noun', 'Tags'),
            getValue: (obj) => { return obj.tags },
            getValueRepr: getTagsValueRepr
          },
          {
            id: 'mbid',
            label: this.$pgettext('*/*/*/Noun', 'MusicBrainz ID'),
            getValue: (obj) => { return obj.mbid }
          },
        ]
      },
      track: {
        label: this.$pgettext('*/*/*', 'Track'),
        icon: 'music',
        getDeleteUrl: (obj) => {
          return `manage/library/tracks/${obj.id}/`
        },
        urls: {
          getDetail: (obj) => { return {name: 'library.tracks.detail', params: {id: obj.id}}},
          getAdminDetail: (obj) => { return {name: 'manage.library.tracks.detail', params: {id: obj.id}}}
        },
        moderatedFields: [
          {
            id: 'title',
            label: this.$pgettext('*/*/*/Noun', 'Title'),
            getValue: (obj) => { return obj.title }
          },
          {
            id: 'position',
            label: this.$pgettext('*/*/*/Short, Noun', 'Position'),
            getValue: (obj) => { return obj.position }
          },
          {
            id: 'copyright',
            label: this.$pgettext('Content/Track/*/Noun', 'Copyright'),
            getValue: (obj) => { return obj.copyright }
          },
          {
            id: 'license',
            label: this.$pgettext('Content/*/*/Noun', 'License'),
            getValue: (obj) => { return obj.license },
          },
          {
            id: 'tags',
            label: this.$pgettext('*/*/*/Noun', 'Tags'),
            getValue: (obj) => { return obj.tags },
            getValueRepr: getTagsValueRepr
          },
          {
            id: 'mbid',
            label: this.$pgettext('*/*/*/Noun', 'MusicBrainz ID'),
            getValue: (obj) => { return obj.mbid }
          },
        ]
      },
      library: {
        label: this.$pgettext('*/*/*', 'Library'),
        icon: 'book',
        getDeleteUrl: (obj) => {
          return `manage/library/libraries/${obj.uuid}/`
        },
        urls: {
          getAdminDetail: (obj) => { return {name: 'manage.library.libraries.detail', params: {id: obj.uuid}}}
        },
        moderatedFields: [
          {
            id: 'name',
            label: this.$pgettext('*/*/*/Noun', 'Name'),
            getValue: (obj) => { return obj.name }
          },
          {
            id: 'description',
            label: this.$pgettext('*/*/*/Noun', 'Description'),
            getValue: (obj) => { return obj.position }
          },
          {
            id: 'privacy_level',
            label: this.$pgettext('*/*/*', 'Visibility'),
            getValue: (obj) => { return obj.privacy_level }
          },
        ]
      },
      playlist: {
        label: this.$pgettext('*/*/*', 'Playlist'),
        icon: 'list',
        urls: {
          getDetail: (obj) => { return {name: 'library.playlists.detail', params: {id: obj.id}}},
          // getAdminDetail: (obj) => { return {name: 'manage.playlists.detail', params: {id: obj.id}}}
        },
        moderatedFields: [
          {
            id: 'name',
            label: this.$pgettext('*/*/*/Noun', 'Name'),
            getValue: (obj) => { return obj.name }
          },
          {
            id: 'privacy_level',
            label: this.$pgettext('*/*/*', 'Visibility'),
            getValue: (obj) => { return obj.privacy_level }
          },
        ]
      },
      account: {
        label: this.$pgettext('*/*/*', 'Account'),
        icon: 'user',
        urls: {
          getAdminDetail: (obj) => { return {name: 'manage.moderation.accounts.detail', params: {id: `${obj.preferred_username}@${obj.domain}`}}}
        },
        moderatedFields: [
          {
            id: 'name',
            label: this.$pgettext('*/*/*/Noun', 'Name'),
            getValue: (obj) => { return obj.name }
          },
          {
            id: 'summary',
            label: this.$pgettext('*/*/*/Noun', 'Bio'),
            getValue: (obj) => { return obj.summary }
          },
        ]
      },
    }
  },

  getConfig () {
    return this.configs[this.objectType]
  },
  getFieldConfig (configs, type, fieldId) {
    let c = configs[type]
    return c.fields.filter((f) => {
      return f.id == fieldId
    })[0]
  },
  getCurrentStateForObj (obj, config) {
    let s = {}
    config.fields.forEach(f => {
      s[f.id] = {value: f.getValue(obj)}
    })
    return s
  },

}
