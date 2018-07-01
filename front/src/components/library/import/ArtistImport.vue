<template>
  <div>
    <h3 class="ui dividing block header">
      <a :href="getMusicbrainzUrl('artist', metadata.id)" target="_blank" title="View on MusicBrainz">{{ metadata.name }}</a>
    </h3>
    <form class="ui form" @submit.prevent="">
      <h6 class="ui header">
        <translate>Filter album types</translate>
      </h6>
      <div class="inline fields">
        <div class="field" v-for="t in availableReleaseTypes">
          <div class="ui checkbox">
            <input type="checkbox" :value="t" v-model="releaseTypes" />
            <label>{{ t }}</label>
          </div>
        </div>
        <div class="field">
          <label><translate>Query template</translate></label>
          <input v-model="customQueryTemplate" />
        </div>
      </div>
    </form>
    <template
      v-for="release in releases">
      <release-import
        :key="release.id"
        :metadata="release"
        :backends="backends"
        :defaultEnabled="false"
        :default-backend-id="defaultBackendId"
        :query-template="customQueryTemplate"
        @import-data-changed="recordReleaseData"
        @enabled="recordReleaseEnabled"
      ></release-import>
      <div class="ui divider"></div>
    </template>
  </div>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import logger from '@/logging'

import ImportMixin from './ImportMixin'
import ReleaseImport from './ReleaseImport'

export default Vue.extend({
  mixins: [ImportMixin],
  components: {
    ReleaseImport
  },
  data () {
    return {
      releaseImportData: [],
      releaseGroupsData: {},
      releases: [],
      releaseTypes: ['Album'],
      availableReleaseTypes: [
        'Album',
        'Live',
        'Compilation',
        'EP',
        'Single',
        'Other']
    }
  },
  created () {
    this.fetchReleaseGroupsData()
  },
  methods: {
    recordReleaseData (release) {
      let existing = this.releaseImportData.filter(r => {
        return r.releaseId === release.releaseId
      })[0]
      if (existing) {
        existing.tracks = release.tracks
      } else {
        this.releaseImportData.push({
          releaseId: release.releaseId,
          enabled: true,
          tracks: release.tracks
        })
      }
    },
    recordReleaseEnabled (release, enabled) {
      let existing = this.releaseImportData.filter(r => {
        return r.releaseId === release.releaseId
      })[0]
      if (existing) {
        existing.enabled = enabled
      } else {
        this.releaseImportData.push({
          releaseId: release.releaseId,
          enabled: enabled,
          tracks: release.tracks
        })
      }
    },
    fetchReleaseGroupsData () {
      let self = this
      this.releaseGroups.forEach(group => {
        let url = 'providers/musicbrainz/releases/browse/' + group.id + '/'
        return axios.get(url).then((response) => {
          logger.default.info('successfully fetched release group', group.id)
          let release = response.data['release-list'].filter(r => {
            return r.status === 'Official'
          })[0]
          self.releaseGroupsData[group.id] = release
          self.releases = self.computeReleaseData()
        }, (response) => {
          logger.default.error('error while fetching release group', group.id)
        })
      })
    },
    computeReleaseData () {
      let self = this
      let releases = []
      this.releaseGroups.forEach(group => {
        let data = self.releaseGroupsData[group.id]
        if (data) {
          releases.push(data)
        }
      })
      return releases
    }
  },
  computed: {
    type () {
      return 'artist'
    },
    releaseGroups () {
      let self = this
      return this.metadata['release-group-list'].filter(r => {
        return self.releaseTypes.indexOf(r.type) !== -1
      }).sort(function (a, b) {
        if (a['first-release-date'] < b['first-release-date']) {
          return -1
        }
        if (a['first-release-date'] > b['first-release-date']) {
          return 1
        }
        return 0
      })
    },
    importData () {
      let releases = this.releaseImportData.filter(r => {
        return r.enabled
      })
      return {
        artistId: this.metadata.id,
        count: releases.reduce(function (a, b) {
          return a + b.tracks.length
        }, 0),
        albums: releases
      }
    }
  },
  watch: {
    releaseTypes (newValue) {
      this.fetchReleaseGroupsData()
    }
  }
})
</script>
