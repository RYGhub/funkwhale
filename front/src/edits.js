export default {
  getConfigs () {
    return {
      track: {
        fields: [
          {
            id: 'title',
            type: 'text',
            required: true,
            label: this.$pgettext('Content/Track/*/Noun', 'Title'),
            getValue: (obj) => { return obj.title }
          },
          {
            id: 'position',
            type: 'text',
            inputType: 'number',
            required: false,
            label: this.$pgettext('*/*/*/Short, Noun', 'Position'),
            getValue: (obj) => { return obj.position }
          },
          {
            id: 'copyright',
            type: 'text',
            required: false,
            label: this.$pgettext('Content/Track/*/Noun', 'Copyright'),
            getValue: (obj) => { return obj.copyright }
          },
          {
            id: 'license',
            type: 'license',
            required: false,
            label: this.$pgettext('Content/*/*/Noun', 'License'),
            getValue: (obj) => { return obj.license },
          },
        ]
      }
    }
  },

  getConfig () {
    return this.configs[this.objectType]
  },

  getCurrentState () {
    let self = this
    let s = {}
    this.config.fields.forEach(f => {
      s[f.id] = {value: f.getValue(self.object)}
    })
    return s
  },
  getCurrentStateForObj (obj, config) {
    let s = {}
    config.fields.forEach(f => {
      s[f.id] = {value: f.getValue(obj)}
    })
    return s
  },

  getCanDelete () {
    if (this.obj.is_applied || this.obj.is_approved) {
      return false
    }
    if (!this.$store.state.auth.authenticated) {
      return false
    }
    return (
      this.obj.created_by.full_username === this.$store.state.auth.fullUsername
      || this.$store.state.auth.availablePermissions['library']
    )
  },
  getCanApprove () {
    if (this.obj.is_applied) {
      return false
    }
    if (!this.$store.state.auth.authenticated) {
      return false
    }
    return this.$store.state.auth.availablePermissions['library']
  },
  getCanEdit () {
    if (!this.$store.state.auth.authenticated) {
      return false
    }
    return this.$store.state.auth.availablePermissions['library']
  },

}
