<template>
  <div v-title="'Import Music'">
    <div class="ui vertical stripe segment">
      <div class="ui top three attached ordered steps">
        <a @click="currentStep = 0" :class="['step', {'active': currentStep === 0}, {'completed': currentStep > 0}]">
          <div class="content">
            <div class="title">{{ $gettext('Import source') }}</div>
            <div class="description">{{ $gettext('Uploaded files or external source') }}</div>
          </div>
        </a>
        <a @click="currentStep = 1" :class="['step', {'active': currentStep === 1}, {'completed': currentStep > 1}]">
          <div class="content">
            <div class="title">{{ $gettext('Metadata') }}</div>
            <div class="description">{{ $gettext('Grab corresponding metadata') }}</div>
          </div>
        </a>
        <a @click="currentStep = 2" :class="['step', {'active': currentStep === 2}, {'completed': currentStep > 2}]">
          <div class="content">
            <div class="title">{{ $gettext('Music') }}</div>
            <div class="description">{{ $gettext('Select relevant sources or files for import') }}</div>
          </div>
        </a>
      </div>
      <div class="ui hidden divider"></div>
      <div class="ui centered buttons">
        <button @click="currentStep -= 1" :disabled="currentStep === 0" class="ui icon button"><i class="left arrow icon"></i>
          {{ $gettext('Previous step') }}
        </button>
        <button @click="nextStep()" v-if="currentStep < 2" class="ui icon button">
          {{ $gettext('Next step') }}
          <i class="right arrow icon"></i>
        </button>
        <button
          @click="$refs.import.launchImport()"
          v-if="currentStep === 2 && currentSource != 'upload'"
          :class="['ui', 'positive', 'icon', {'loading': isImporting}, 'button']"
          :disabled="isImporting || importData.count === 0"
          >
            <translate
              :translate-params="{count: importData.count || 0}"
              :translate-n="importData.count || 0"
              translate-plural="Import %{ count } tracks">
              Import %{ count } track
            </translate>
            <i class="check icon"></i>
          </button>
        <button
          v-else-if="currentStep === 2 && currentSource === 'upload'"
          @click="$router.push({name: 'library.import.batches.detail', params: {id: importBatch.id}})"
          :class="['ui', 'positive', 'icon', {'disabled': !importBatch}, 'button']"
          :disabled="!importBatch"
          >
            {{ $gettext('Finish import' )}}
            <i class="check icon"></i>
          </button>
      </div>
      <div class="ui hidden divider"></div>
      <div class="ui attached segment">
        <template v-if="currentStep === 0">
          <p>{{ $gettext('First, choose where you want to import the music from') }}</p>
          <form class="ui form">
            <div class="field">
              <div class="ui radio checkbox">
                <input type="radio" id="external" value="external" v-model="currentSource">
                <label for="external">
                  {{ $gettext('External source. Supported backends') }}
                  <div v-for="backend in backends" class="ui basic label">
                    <i v-if="backend.icon" :class="[backend.icon, 'icon']"></i>
                    {{ backend.label }}
                  </div>
                </label>
              </div>
            </div>
            <div class="field">
              <div class="ui radio checkbox">
                <input type="radio" id="upload" value="upload" v-model="currentSource">
                <label for="upload">{{ $gettext('File upload') }}</label>
              </div>
            </div>
          </form>
        </template>
        <div v-if="currentStep === 1" class="ui stackable two column grid">
          <div class="column">
            <form class="ui form" @submit.prevent="">
              <div class="field">
                <label>{{ $gettext('Search an entity you want to import:') }}</label>
                <metadata-search
                  :mb-type="mbType"
                  :mb-id="mbId"
                  @id-changed="updateId"
                  @type-changed="updateType"></metadata-search>
              </div>
            </form>
            <div class="ui horizontal divider">{{ $gettext('Or') }}</div>
            <form class="ui form" @submit.prevent="">
              <div class="field">
                <label>{{ $gettext('Input a MusicBrainz ID manually:') }}</label>
                <input type="text" v-model="currentId" />
              </div>
            </form>
            <div class="ui hidden divider"></div>
            <template v-if="currentType && currentId">
              <h4 class="ui header">
                {{ $gettext('You will import:') }}
              </h4>
              <component
                :mbId="currentId"
                :is="metadataComponent"
                @metadata-changed="this.updateMetadata"
                ></component>
            </template>
            <p>{{ $gettext('You can also skip this step and enter metadata manually.') }}</p>
          </div>
          <div class="column">
            <h5 class="ui header">What is metadata?</h5>
            <template v-translate>
              Metadata is the data related to the music you want to import. This includes all the information about the artists, albums and tracks. In order to have a high quality library, it is recommended to grab data from the
              <a href="https://musicbrainz.org" target="_blank">
                MusicBrainz
              </a>
              project, which you can think about as the Wikipedia of music.
            </template>
          </div>
        </div>
        <div v-if="currentStep === 2">
          <file-upload
            ref="import"
            @batch-created="updateBatch"
            v-if="currentSource == 'upload'"
            ></file-upload>

          <component
            ref="import"
            v-if="currentSource == 'external'"
            :request="currentRequest"
            :metadata="metadata"
            :is="importComponent"
            :backends="backends"
            :default-backend-id="backends[0].id"
            @import-data-changed="updateImportData"
            @import-state-changed="updateImportState"
            ></component>
        </div>
      </div>
    </div>
    <div class="ui vertical stripe segment" v-if="currentRequest">
      <h3 class="ui header">
        {{ $gettext('Music request') }}
      </h3>
      <p>{{ $gettext('This import will be associated with the music request below. After the import is finished, the request will be marked as fulfilled.') }}</p>
      <request-card :request="currentRequest" :import-action="false"></request-card>

    </div>
  </div>
</template>

<script>

import RequestCard from '@/components/requests/Card'
import MetadataSearch from '@/components/metadata/Search'
import ReleaseCard from '@/components/metadata/ReleaseCard'
import ArtistCard from '@/components/metadata/ArtistCard'
import ReleaseImport from './ReleaseImport'
import FileUpload from './FileUpload'
import ArtistImport from './ArtistImport'

import axios from 'axios'
import router from '@/router'
import $ from 'jquery'

export default {
  components: {
    MetadataSearch,
    ArtistCard,
    ReleaseCard,
    ArtistImport,
    ReleaseImport,
    FileUpload,
    RequestCard
  },
  props: {
    mbType: {type: String, required: false},
    request: {type: String, required: false},
    source: {type: String, required: false},
    mbId: {type: String, required: false}
  },
  data: function () {
    return {
      currentRequest: null,
      currentType: this.mbType || 'artist',
      currentId: this.mbId,
      currentStep: 0,
      currentSource: this.source,
      metadata: {},
      isImporting: false,
      importBatch: null,
      importData: {
        tracks: []
      },
      backends: [
        {
          id: 'youtube',
          label: 'YouTube',
          icon: 'youtube'
        }
      ]
    }
  },
  created () {
    if (this.request) {
      this.fetchRequest(this.request)
    }
    if (this.currentSource) {
      this.currentStep = 1
    }
  },
  mounted: function () {
    $(this.$el).find('.ui.checkbox').checkbox()
  },
  methods: {
    updateRoute () {
      router.replace({
        query: {
          source: this.currentSource,
          type: this.currentType,
          id: this.currentId,
          request: this.request
        }
      })
    },
    updateImportData (newValue) {
      this.importData = newValue
    },
    updateImportState (newValue) {
      this.isImporting = newValue
    },
    updateMetadata (newValue) {
      this.metadata = newValue
    },
    updateType (newValue) {
      this.currentType = newValue
    },
    updateId (newValue) {
      this.currentId = newValue
    },
    updateBatch (batch) {
      this.importBatch = batch
    },
    fetchRequest (id) {
      let self = this
      axios.get(`requests/import-requests/${id}`).then((response) => {
        self.currentRequest = response.data
      })
    },
    nextStep () {
      if (this.currentStep === 0 && this.currentSource === 'upload') {
        // we skip metadata directly
        this.currentStep += 2
      } else {
        this.currentStep += 1
      }
    }
  },
  computed: {
    metadataComponent () {
      if (this.currentType === 'artist') {
        return 'ArtistCard'
      }
      if (this.currentType === 'release') {
        return 'ReleaseCard'
      }
      if (this.currentType === 'recording') {
        return 'RecordingCard'
      }
    },
    importComponent () {
      if (this.currentType === 'artist') {
        return 'ArtistImport'
      }
      if (this.currentType === 'release') {
        return 'ReleaseImport'
      }
      if (this.currentType === 'recording') {
        return 'RecordingImport'
      }
    }
  },
  watch: {
    currentType (newValue) {
      this.currentId = ''
      this.updateRoute()
    },
    currentId (newValue) {
      this.updateRoute()
    }
  }
}
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
