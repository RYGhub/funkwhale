<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoadingLibrary" :class="['ui', {'active': isLoadingLibrary}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading library data...</translate></div>
    </div>
    <detail-area v-else :library="library">
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
