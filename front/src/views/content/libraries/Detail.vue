<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoadingLibrary" :class="['ui', {'active': isLoadingLibrary}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading library data...</translate></div>
    </div>
    <detail-area v-else :library="library">
      <div slot="header">
        <h2 class="ui header"><translate>Manage</translate></h2>
        <p><a @click="hiddenForm = !hiddenForm">
          <i class="pencil icon" />
          <translate>Edit library</translate>
        </a></p>
        <library-form v-if="!hiddenForm" :library="library" @updated="libraryUpdated" @deleted="libraryDeleted" />
        <div class="ui hidden divider"></div>
        <div class="ui form">
          <div class="field">
            <label><translate>Sharing link</translate></label>
            <p><translate>Share this link with other users so they can request an access to your library.</translate></p>
            <copy-input :value="library.fid" />
          </div>
        </div>
      </div>
      <h2><translate>Tracks</translate></h2>
      <library-files-table :filters="{library: library.uuid}"></library-files-table>
    </detail-area>
  </div>
</template>

<script>
import DetailMixin from './DetailMixin'
import DetailArea from './DetailArea'
import LibraryForm from './Form'
import LibraryFilesTable from './FilesTable'

export default {
  mixins: [DetailMixin],
  components: {
    DetailArea,
    LibraryForm,
    LibraryFilesTable
  },
  data () {
    return {
      hiddenForm: true
    }
  },
  methods: {
    libraryUpdated () {
      this.hiddenForm = true
      this.fetch()
    },
    libraryDeleted () {
      this.$router.push({
        name: 'content.libraries.index'
      })
    }
  }
}
</script>
