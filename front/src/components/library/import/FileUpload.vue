<template>
  <div>
    <div v-if="batch" class="ui two buttons">
      <file-upload-widget
        class="ui icon button"
        :post-action="uploadUrl"
        :multiple="true"
        :size="1024 * 1024 * 30"
        :data="uploadData"
        :drop="true"
        extensions="ogg,mp3"
        accept="audio/*"
        v-model="files"
        name="audio_file"
        :thread="3"
        @input-filter="inputFilter"
        @input-file="inputFile"
        ref="upload">
        <i class="upload icon"></i>
        Select files to upload...
    </file-upload-widget>
      <button class="ui icon teal button" v-if="!$refs.upload || !$refs.upload.active" @click.prevent="$refs.upload.active = true">
        <i class="play icon" aria-hidden="true"></i>
        Start Upload
      </button>
      <button type="button" class="ui icon yellow button" v-else @click.prevent="$refs.upload.active = false">
        <i class="pause icon" aria-hidden="true"></i>
        Stop Upload
      </button>
    </div>
    <div class="ui hidden divider"></div>
    <p>
      Once all your files are uploaded, simply head over  <router-link :to="{name: 'library.import.batches.detail', params: {id: batch.id }}">import detail page</router-link> to check the import status.
    </p>
    <table class="ui single line table">
      <thead>
        <tr>
          <th>File name</th>
          <th>Size</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(file, index) in files" :key="file.id">
          <td>{{ file.name }}</td>
          <td>{{ file.size }}</td>
          <td>
            <span v-if="file.error" class="ui red label">
              {{ file.error }}
            </span>
            <span v-else-if="file.success" class="ui green label">Success</span>
            <span v-else-if="file.active" class="ui yellow label">Uploading...</span>
            <template v-else>
              <span class="ui label">Pending</span>
              <button class="ui tiny basic red icon button" @click.prevent="$refs.upload.remove(file)"><i class="delete icon"></i></button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Vue from 'vue'
import logger from '@/logging'
import FileUploadWidget from './FileUploadWidget'
import config from '@/config'

export default {
  components: {
    FileUploadWidget
  },
  data () {
    return {
      files: [],
      uploadUrl: config.API_URL + 'import-jobs/',
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
        if (['ogg', 'mp3'].indexOf(extension) < 0) {
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
      let url = config.API_URL + 'import-batches/'
      let resource = Vue.resource(url)
      resource.save({}, {}).then((response) => {
        self.batch = response.data
      }, (response) => {
        logger.default.error('error while launching creating batch')
      })
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
