<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoadingLibrary" :class="['ui', {'active': isLoadingLibrary}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading library data…</translate></div>
    </div>
    <detail-area v-else :library="library">
      <file-upload ref="fileupload" :default-import-reference="defaultImportReference" :library="library" />
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
  },
  beforeRouteLeave (to, from, next){
    if (this.$refs.fileupload.hasActiveUploads){
      const answer = window.confirm('This page is asking you to confirm that you want to leave - data you have entered may not be saved.')
      if (answer) {
        next()
      } else {
        next(false)
      }
    }
    else{
      next()
    }
  }
}
</script>
