<template>
  <div class="ui segment">
    <h3 class="ui header"><translate>Current usage</translate></h3>
    <div v-if="isLoading" :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading usage data...</translate></div>
    </div>
    <div :class="['ui', {'success': progress < 60}, {'yellow': progress >= 60 && progress < 96}, {'error': progress >= 95}, 'progress']">
      <div class="bar">
        <div class="progress">{{ progress }}%</div>
      </div>
      <div class="label" v-if="quotaStatus">
        <translate :translate-params="{max: humanSize(quotaStatus.max * 1000 * 1000), current: humanSize(quotaStatus.current * 1000 * 1000)}">%{ current } used on %{ max } allowed</translate>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <div v-if="quotaStatus" class="ui stackable three column grid">
      <div v-if="quotaStatus.pending > 0" class="column">
        <div class="ui tiny yellow statistic">
          <div class="value">
            {{ humanSize(quotaStatus.pending * 1000 * 1000) }}
          </div>
          <div class="label">
            <translate>Pending files</translate>
          </div>
        </div>
        <div>
          <router-link
            class="ui basic blue tiny button"
            :to="{name: 'content.libraries.files', query: {q: compileTokens([{field: 'status', value: 'pending'}])}}">
            <translate>View files</translate>
          </router-link>

          <dangerous-button
            color="grey"
            class="basic tiny"
            :action="purgePendingFiles">
            <translate>Purge</translate>
            <p slot="modal-header"><translate>Purge pending files?</translate></p>
            <p slot="modal-content"><translate>This will remove tracks that were uploaded but not processed yet. This will remove those files completely and you will regain the corresponding quota.</translate></p>
            <p slot="modal-confirm"><translate>Purge</translate></p>
          </dangerous-button>
        </div>
      </div>
      <div v-if="quotaStatus.skipped > 0" class="column">
        <div class="ui tiny grey statistic">
          <div class="value">
            {{ humanSize(quotaStatus.skipped * 1000 * 1000) }}
          </div>
          <div class="label">
            <translate>Skipped files</translate>
          </div>
        </div>
        <div>
          <router-link
            class="ui basic blue tiny button"
            :to="{name: 'content.libraries.files', query: {q: compileTokens([{field: 'status', value: 'skipped'}])}}">
            <translate>View files</translate>
          </router-link>
          <dangerous-button
            color="grey"
            class="basic tiny"
            :action="purgeSkippedFiles">
            <translate>Purge</translate>
            <p slot="modal-header"><translate>Purge skipped files?</translate></p>
            <p slot="modal-content"><translate>This will remove tracks that were uploaded but skipped during import processes for various reasons. This will remove those files completely and you will regain the corresponding quota.</translate></p>
            <p slot="modal-confirm"><translate>Purge</translate></p>
          </dangerous-button>
        </div>
      </div>
      <div v-if="quotaStatus.errored > 0" class="column">
        <div class="ui tiny red statistic">
          <div class="value">
            {{ humanSize(quotaStatus.errored * 1000 * 1000) }}
          </div>
          <div class="label">
            <translate>Errored files</translate>
          </div>
        </div>
        <div>
          <router-link
            class="ui basic blue tiny button"
            :to="{name: 'content.libraries.files', query: {q: compileTokens([{field: 'status', value: 'errored'}])}}">
            <translate>View files</translate>
          </router-link>
          <dangerous-button
            color="grey"
            class="basic tiny"
            :action="purgeErroredFiles">
            <translate>Purge</translate>
            <p slot="modal-header"><translate>Purge errored files?</translate></p>
            <p slot="modal-content"><translate>This will remove tracks that were uploaded but failed to be process by the server. This will remove those files completely and you will regain the corresponding quota.</translate></p>
            <p slot="modal-confirm"><translate>Purge</translate></p>
          </dangerous-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
import $ from 'jquery'
import {humanSize} from '@/filters'
import {compileTokens} from '@/search'

export default {
  data () {
    return {
      quotaStatus: null,
      isLoading: false,
      humanSize,
      compileTokens
    }
  },
  created () {
    this.fetch()
  },
  methods: {
    fetch () {
      let self = this
      self.isLoading = true
      axios.get('users/users/me/').then((response) => {
        self.quotaStatus = response.data.quota_status
        self.isLoading = false
      })
    },
    purge (status) {
      let self = this
      let payload = {
        action: 'delete',
        objects: 'all',
        filters: {
          import_status: status
        }
      }
      axios.post('uploads/action/', payload).then((response) => {
        self.fetch()
      })
    },
    purgeSkippedFiles () {
      this.purge('skipped')
    },
    purgePendingFiles () {
      this.purge('pending')
    },
    purgeErroredFiles () {
      this.purge('errored')
    },
    updateProgressBar () {
      $(this.$el).find('.ui.progress').progress({
        percent: this.progress,
        showActivity: false
      })
    }
  },
  computed: {
    progress () {
      if (!this.quotaStatus) {
        return 0
      }
      return Math.min(parseInt(this.quotaStatus.current * 100 / this.quotaStatus.max), 100)
    }
  },
  watch: {
    progress () {
      this.updateProgressBar()
    }
  }
}
</script>
