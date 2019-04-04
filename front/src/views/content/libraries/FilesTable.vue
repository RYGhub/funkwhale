<template>
  <div>
    <div class="ui inline form">
      <div class="fields">
        <div class="ui six wide field">
          <label><translate translate-context="Content/Search/Input.Label/Noun">Search</translate></label>
          <form @submit.prevent="search.query = $refs.search.value">
            <input name="search" ref="search" type="text" :value="search.query" :placeholder="labels.searchPlaceholder" />
          </form>
        </div>
        <div class="field">
          <label><translate translate-context="Content/Library/*/Noun">Import status</translate></label>
          <select class="ui dropdown" @change="addSearchToken('status', $event.target.value)" :value="getTokenValue('status', '')">
            <option value=""><translate translate-context="Content/*/Dropdown">All</translate></option>
            <option value="pending"><translate translate-context="Content/Library/*/Short">Pending</translate></option>
            <option value="skipped"><translate translate-context="Content/Library/*">Skipped</translate></option>
            <option value="errored"><translate translate-context="Content/Library/Dropdown">Failed</translate></option>
            <option value="finished"><translate translate-context="Content/Library/*">Finished</translate></option>
          </select>
        </div>
        <div class="field">
          <label><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering</translate></label>
          <select class="ui dropdown" v-model="ordering">
            <option v-for="option in orderingOptions" :value="option[0]">
              {{ sharedLabels.filters[option[1]] }}
            </option>
          </select>
        </div>
        <div class="field">
          <label><translate translate-context="Content/Search/Dropdown.Label/Noun">Ordering direction</translate></label>
          <select class="ui dropdown" v-model="orderingDirection">
            <option value="+"><translate translate-context="Content/Search/Dropdown">Ascending</translate></option>
            <option value="-"><translate translate-context="Content/Search/Dropdown">Descending</translate></option>
          </select>
        </div>
      </div>
    </div>
    <modal :show.sync="showUploadDetailModal">
      <div class="header">
        <translate translate-context="Popup/Import/Title">Import detail</translate>
      </div>
      <div class="content" v-if="detailedUpload">
        <div class="description">
          <div class="ui message" v-if="detailedUpload.import_status === 'pending'">
            <translate translate-context="Popup/Import/Message">Upload is still pending and will soon be processed by the server.</translate>
          </div>
          <div class="ui success message" v-if="detailedUpload.import_status === 'finished'">
            <translate translate-context="Popup/Import/Message">Upload was successfully processed by the server.</translate>
          </div>
          <div class="ui warning message" v-if="detailedUpload.import_status === 'skipped'">
            <translate translate-context="Popup/Import/Message">Upload was skipped because a similar one is already available in one of your libraries.</translate>
          </div>
          <div class="ui error message" v-if="detailedUpload.import_status === 'errored'">
            <translate translate-context="Popup/Import/Message">An error occured during upload processing. You will find more information below.</translate>
          </div>
          <template v-if="detailedUpload.import_status === 'errored'">
            <table class="ui very basic collapsing celled table">
              <tbody>
                <tr>
                  <td>
                    <translate translate-context="Popup/Import/Table.Label/Noun">Error type</translate>
                  </td>
                  <td>
                    {{ getErrorData(detailedUpload).label }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Popup/Import/Table.Label/Noun">Error detail</translate>
                  </td>
                  <td>
                    {{ getErrorData(detailedUpload).detail }}
                    <ul v-if="getErrorData(detailedUpload).errorRows.length > 0">
                      <li v-for="row in getErrorData(detailedUpload).errorRows">
                        {{ row.key}}: {{ row.value}}
                      </li>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Popup/Import/Table.Label/Noun">Getting help</translate>
                  </td>
                  <td>
                    <ul>
                      <li>
                        <a :href="getErrorData(detailedUpload).documentationUrl" target="_blank">
                          <translate translate-context="Popup/Import/Table.Label/Value">Read our documentation for this error</translate>
                        </a>
                      </li>
                      <li>
                        <a :href="getErrorData(detailedUpload).supportUrl" target="_blank">
                          <translate translate-context="Popup/Import/Table.Label/Value">Open a support thread (include the debug information below in your message)</translate>
                        </a>
                      </li>
                    </ul>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Popup/Import/Table.Label/Noun">Debug information</translate>
                  </td>
                  <td>
                    <div class="ui form">
                      <textarea class="ui textarea" rows="10" :value="getErrorData(detailedUpload).debugInfo"></textarea>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>
      </div>
      <div class="actions">
        <div class="ui deny button">
          <translate translate-context="*/*/Button.Label/Verb">Close</translate>
        </div>
      </div>
    </modal>
    <div class="dimmable">
      <div v-if="isLoading" class="ui active inverted dimmer">
          <div class="ui loader"></div>
      </div>
      <action-table
        v-if="result"
        @action-launched="fetchData"
        :id-field="'uuid'"
        :objects-data="result"
        :custom-objects="customObjects"
        :actions="actions"
        :refreshable="true"
        :needs-refresh="needsRefresh"
        :action-url="'uploads/action/'"
        @refresh="fetchData"
        :filters="actionFilters">
        <template slot="header-cells">
          <th><translate translate-context="Content/Track/*/Noun">Title</translate></th>
          <th><translate translate-context="*/*/*/Noun">Artist</translate></th>
          <th><translate translate-context="*/*/*">Album</translate></th>
          <th><translate translate-context="*/*/*/Noun">Upload date</translate></th>
          <th><translate translate-context="Content/Library/*/Noun">Import status</translate></th>
          <th><translate translate-context="Content/*/*">Duration</translate></th>
          <th><translate translate-context="Content/Library/*/in MB">Size</translate></th>
        </template>
        <template slot="row-cells" slot-scope="scope">
          <template v-if="scope.obj.track">
            <td>
              <span :title="scope.obj.track.title">{{ scope.obj.track.title|truncate(25) }}</span>
            </td>
            <td>
              <span class="discrete link" @click="addSearchToken('artist', scope.obj.track.artist.name)" :title="scope.obj.track.artist.name">{{ scope.obj.track.artist.name|truncate(20) }}</span>
            </td>
            <td>
              <span class="discrete link" @click="addSearchToken('album', scope.obj.track.album.title)" :title="scope.obj.track.album.title">{{ scope.obj.track.album.title|truncate(20) }}</span>
            </td>
          </template>
          <template v-else>
            <td :title="scope.obj.source">{{ scope.obj.source | truncate(25) }}</td>
            <td></td>
            <td></td>
          </template>
          <td>
            <human-date :date="scope.obj.creation_date"></human-date>
          </td>
          <td>
            <span class="discrete link" @click="addSearchToken('status', scope.obj.import_status)" :title="labels.importStatuses[scope.obj.import_status].help">
              {{ labels.importStatuses[scope.obj.import_status].label }}
            </span>
            <button class="ui tiny basic icon button" :title="labels.statusDetailTitle" @click="detailedUpload = scope.obj; showUploadDetailModal = true">
              <i class="question circle outline icon"></i>
            </button>
          </td>
          <td v-if="scope.obj.duration">
            {{ time.parse(scope.obj.duration) }}
          </td>
          <td v-else>
            <translate translate-context="*/*/*">N/A</translate>
          </td>
          <td v-if="scope.obj.size">
            {{ scope.obj.size | humanSize }}
          </td>
          <td v-else>
            <translate translate-context="*/*/*">N/A</translate>
          </td>
        </template>
      </action-table>
    </div>
    <div>
      <pagination
        v-if="result && result.count > paginateBy"
        @page-changed="selectPage"
        :compact="true"
        :current="page"
        :paginate-by="paginateBy"
        :total="result.count"
        ></pagination>

      <span v-if="result && result.results.length > 0">
        <translate translate-context="Content/*/Paragraph"
          :translate-params="{start: ((page-1) * paginateBy) + 1, end: ((page-1) * paginateBy) + result.results.length, total: result.count}">
          Showing results %{ start }-%{ end } on %{ total }
        </translate>
      </span>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import _ from '@/lodash'
import time from '@/utils/time'
import {normalizeQuery, parseTokens} from '@/search'

import Pagination from '@/components/Pagination'
import ActionTable from '@/components/common/ActionTable'
import OrderingMixin from '@/components/mixins/Ordering'
import TranslationsMixin from '@/components/mixins/Translations'
import SmartSearchMixin from '@/components/mixins/SmartSearch'
import Modal from '@/components/semantic/Modal'

function getErrors(payload) {
  let errors = []
  for (var k in payload) {
    if (payload.hasOwnProperty(k)) {
      let value = payload[k]
      if (Array.isArray(value)) {
        errors.push({
          key: k,
          value: value.join(', ')
        })
      } else {
        // possibly artists, so nested errors
        if (typeof value === 'object') {
          getErrors(value).forEach((e) => {
            errors.push({
              key: `${k} / ${e.key}`,
              value: e.value
            })
          })
        }
      }
    }
  }
  return errors
}
export default {
  mixins: [OrderingMixin, TranslationsMixin, SmartSearchMixin],
  props: {
    filters: {type: Object, required: false},
    needsRefresh: {type: Boolean, required: false, default: false},
    customObjects: {type: Array, required: false, default: () => { return [] }}
  },
  components: {
    Pagination,
    ActionTable,
    Modal
  },
  data () {
    return {
      time,
      detailedUpload: null,
      showUploadDetailModal: false,
      isLoading: false,
      result: null,
      page: 1,
      paginateBy: 25,
      search: {
        query: this.defaultQuery,
        tokens: parseTokens(normalizeQuery(this.defaultQuery))
      },
      orderingDirection: '-',
      ordering: 'creation_date',
      orderingOptions: [
        ['creation_date', 'creation_date'],
        ['title', 'track_title'],
        ['size', 'size'],
        ['duration', 'duration'],
        ['bitrate', 'bitrate'],
        ['album_title', 'album_title'],
        ['artist_name', 'artist_name']
      ]
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.$emit('fetch-start')
      let params = _.merge({
        'page': this.page,
        'page_size': this.paginateBy,
        'ordering': this.getOrderingAsString(),
        'q': this.search.query
      }, this.filters || {})
      let self = this
      self.isLoading = true
      self.checked = []
      axios.get('/uploads/', {params: params}).then((response) => {
        self.result = response.data
        self.isLoading = false
      }, error => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    selectPage: function (page) {
      this.page = page
    },
    getErrorData (upload) {
      let payload = upload.import_details || {}
      let d = {
        supportUrl: 'https://governance.funkwhale.audio/g/246YOJ1m/funkwhale-support',
        errorRows: []
      }
      if (!payload.error_code) {
        d.errorCode = 'unknown_error'
      } else {
        d.errorCode = payload.error_code
      }
      d.documentationUrl = `https://docs.funkwhale.audio/users/upload.html#${d.errorCode}`
      if (d.errorCode === 'invalid_metadata') {
        d.label = this.$pgettext('Popup/Import/Error.Label', 'Invalid metadata')
        d.detail = this.$pgettext('Popup/Import/Error.Label', 'The metadata included in the file is invalid or some mandatory fields are missing.')
        let detail = payload.detail || {}
        d.errorRows = getErrors(detail)
      } else {
        d.label = this.$pgettext('Popup/Import/Error.Label', 'Unkwown error')
        d.detail = this.$pgettext('Popup/Import/Error.Label', 'An unkwown error occured')
      }
      let debugInfo = {
        source: upload.source,
        ...payload,
      }
      d.debugInfo = JSON.stringify(debugInfo, null, 4)
      return d
    }
  },
  computed: {
    labels () {
      return {
        searchPlaceholder: this.$pgettext('Content/Library/Input.Placeholder', 'Search by title, artist, album…'),
        statusDetailTitle: this.$pgettext('Content/Library/Link.Title', 'Click to display more information about the import process for this upload'),
        importStatuses: {
          skipped: {
            label: this.$pgettext('Content/Library/*', 'Skipped'),
            help: this.$pgettext('Content/Library/Help text', 'This track is already present in one of your libraries'),
          },
          pending: {
            label: this.$pgettext('Content/Library/*/Short', 'Pending'),
            help: this.$pgettext('Content/Library/Help text', 'This track has been uploaded, but hasn\'t been processed by the server yet'),
          },
          errored: {
            label: this.$pgettext('Content/Library/Table/Short', 'Errored'),
            help: this.$pgettext('Content/Library/Help text', 'This track could not be processed, please it is tagged correctly'),
          },
          finished: {
            label: this.$pgettext('Content/Library/*', 'Finished'),
            help: this.$pgettext('Content/Library/Help text', 'Imported'),
          },
        }
      }
    },
    actionFilters () {
      var currentFilters = {
        q: this.search.query
      }
      if (this.filters) {
        return _.merge(currentFilters, this.filters)
      } else {
        return currentFilters
      }
    },
    actions () {
      let deleteMsg = this.$pgettext('*/*/*/Verb', 'Delete')
      let relaunchMsg = this.$pgettext('Content/Library/Dropdown/Verb', 'Restart import')
      return [
        {
          name: 'delete',
          label: deleteMsg,
          isDangerous: true,
          allowAll: true
        },
        {
          name: 'relaunch_import',
          label: relaunchMsg,
          isDangerous: true,
          allowAll: true,
          filterCheckable: f => {
            return f.import_status != 'finished'
          }
        }
      ]
    }
  },
  watch: {
    orderingDirection: function () {
      this.page = 1
      this.fetchData()
    },
    page: function () {
      this.fetchData()
    },
    ordering: function () {
      this.page = 1
      this.fetchData()
    },
    search (newValue) {
      this.page = 1
      this.fetchData()
    }
  }
}
</script>
