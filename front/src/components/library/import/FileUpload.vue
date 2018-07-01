<template>
  <div>
    <div v-if="batch" class="ui container">
      <div class="ui message">
        <translate>Ensure your music files are properly tagged before uploading them.</translate>
        <a href="http://picard.musicbrainz.org/" target='_blank'><translate>We recommend using Picard for that purpose.</translate></a>
      </div>
      <file-upload-widget
        :class="['ui', 'icon', 'left', 'floated', 'button']"
        :post-action="uploadUrl"
        :multiple="true"
        :data="uploadData"
        :drop="true"
        extensions="ogg,mp3,flac"
        accept="audio/*"
        v-model="files"
        name="audio_file"
        :thread="3"
        @input-filter="inputFilter"
        @input-file="inputFile"
        ref="upload">
        <i class="upload icon"></i>
        <translate>Select files to upload...</translate>
    </file-upload-widget>
      <button
        :class="['ui', 'right', 'floated', 'icon', {disabled: files.length === 0}, 'button']"
        v-if="!$refs.upload || !$refs.upload.active" @click.prevent="startUpload()">
        <i class="play icon" aria-hidden="true"></i>
        <translate>Start Upload</translate>
      </button>
      <button type="button" class="ui right floated icon yellow button" v-else @click.prevent="$refs.upload.active = false">
        <i class="pause icon" aria-hidden="true"></i>
        <translate>Stop Upload</translate>
      </button>
    </div>
    <div class="ui hidden clearing divider"></div>
    <template v-if="batch"><translate>Once all your files are uploaded, simply click the following button to check the import status.</translate></template>
    <router-link class="ui basic button" v-if="batch" :to="{name: 'library.import.batches.detail', params: {id: batch.id }}">
      <translate>Import detail page</translate>
    </router-link>
    <table class="ui single line table">
      <thead>
        <tr>
          <th><translate>File name</translate></th>
          <th><translate>Size</translate></th>
          <th><translate>Status</translate></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(file, index) in files" :key="file.id">
          <td>{{ file.name }}</td>
          <td>{{ file.size | humanSize }}</td>
          <td>
            <span v-if="file.error" class="ui red label">
              {{ file.error }}
            </span>
            <span v-else-if="file.success" class="ui green label"><translate>Success</translate></span>
            <span v-else-if="file.active" class="ui yellow label"><translate>Uploading...</translate></span>
            <template v-else>
              <span class="ui label"><translate>Pending</translate></span>
              <button class="ui tiny basic red icon button" @click.prevent="$refs.upload.remove(file)"><i class="delete icon"></i></button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'
import FileUploadWidget from './FileUploadWidget'

export default {
  components: {
    FileUploadWidget
  },
  data () {
    return {
      files: [],
      uploadUrl: '/api/v1/import-jobs/',
      batch: null
    }
  },
  mounted: function () {
    this.createBatch()
  },
  methods: {
    inputFilter (newFile, oldFile, prevent) {
      if (newFile && !oldFile) {
        let extension = newFile.name.split('.').pop()
        if (['ogg', 'mp3', 'flac'].indexOf(extension) < 0) {
          prevent()
        }
      }
    },
    inputFile (newFile, oldFile) {
      if (newFile && !oldFile) {
        // add
        if (!this.batch) {
          this.createBatch()
        }
      }
      if (newFile && oldFile) {
        // update
      }
      if (!newFile && oldFile) {
        // remove
      }
    },
    createBatch () {
      let self = this
      return axios.post('import-batches/', {}).then((response) => {
        self.batch = response.data
      }, (response) => {
        logger.default.error('error while launching creating batch')
      })
    },
    startUpload () {
      this.$emit('batch-created', this.batch)
      this.$refs.upload.active = true
    }
  },
  computed: {
    batchId: function () {
      if (this.batch) {
        return this.batch.id
      }
      return null
    },
    uploadData: function () {
      return {
        'batch': this.batchId,
        'source': 'file://'
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
