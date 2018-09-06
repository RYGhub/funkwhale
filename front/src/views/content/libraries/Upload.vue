<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoadingLibrary" :class="['ui', {'active': isLoadingLibrary}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading library data...</translate></div>
    </div>
    <detail-area v-else :library="library">
      <div slot="header">
        <h2 class="ui header"><translate>Upload new tracks</translate></h2>
        <div class="ui message">
          <p><translate>You are about to upload music to your library. Before proceeding, please ensure that:</translate></p>
          <ul>
            <li v-if="library.privacy_level != 'me'">
              You are not uploading copyrighted content in a public library, otherwise you may be infringing the law
            </li>
            <li>
              <translate>The music files you are uploading are tagged properly:</translate>
              <a href="http://picard.musicbrainz.org/" target='_blank'><translate>we recommend using Picard for that purpose</translate></a>
            </li>
            <li>
              <translate>The uploaded music files are in OGG, Flac or MP3 format</translate>
            </li>
          </ul>
        </div>
      </div>
      <file-upload :default-import-reference="defaultImportReference" :library="library" />
    </detail-area>
  </div>
</template>

<script>
import DetailMixin from './DetailMixin'
import DetailArea from './DetailArea'

import FileUpload from '@/components/library/FileUpload'
export default {
  mixins: [DetailMixin],
  props: ['defaultImportReference'],
  components: {
    DetailArea,
    FileUpload
  }
}
</script>
