<template>
  <div class="ui fluid card">
    <div class="content">
      <div class="header">
        {{ library.name }}
        <span
          v-if="library.privacy_level === 'me'"
          class="right floated"
          :data-tooltip="labels.tooltips.me">
          <i class="small lock icon"></i>
        </span>
        <span
          v-else-if="library.privacy_level === 'everyone'"
          class="right floated"
          :data-tooltip="labels.tooltips.everyone">
          <i class="small globe icon"></i>
        </span>
      </div>
      <div class="meta">
        <span>
          <i class="small outline clock icon" />
          <human-date :date="library.creation_date" />
        </span>
      </div>
      <div class="meta">
        <i class="music icon"></i>
        <translate :translate-params="{count: library.uploads_count}" :translate-n="library.uploads_count" translate-plural="%{ count } tracks">%{ count } tracks</translate>
      </div>
      <div v-if="latestScan" class="meta">
        <template v-if="latestScan.status === 'pending'">
          <i class="hourglass icon"></i>
          <translate>Scan pending</translate>
        </template>
        <template v-if="latestScan.status === 'scanning'">
          <i class="loading spinner icon"></i>
          <translate :translate-params="{progress: scanProgress}">Scanning... (%{ progress }%)</translate>
        </template>
        <template v-else-if="latestScan.status === 'errored'">
          <i class="red download icon"></i>
          <translate>Error during scan</translate>
        </template>
        <template v-else-if="latestScan.status === 'finished' && latestScan.errored_files === 0">
          <i class="green download icon"></i>
          <translate>Scanned successfully</translate>
        </template>
        <template v-else-if="latestScan.status === 'finished' && latestScan.errored_files > 0">
          <i class="yellow download icon"></i>
          <translate>Scanned with errors</translate>
        </template>
        <span class="link right floated" @click="showScan = !showScan">
          <translate>Details</translate>
          <i v-if="showScan" class="angle down icon" />
          <i v-else class="angle right icon" />
        </span>
        <div v-if="showScan">
          <template v-if="latestScan.modification_date">
            <translate>Last update:</translate><human-date :date="latestScan.modification_date" /><br />
          </template>
          <translate>Errored tracks:</translate> {{ latestScan.errored_files }}
        </div>
      </div>
      <div v-if="canLaunchScan" class="clearfix">
        <span class="right floated link" @click="launchScan">
          <translate>Launch scan</translate> <i class="paper plane icon" />
        </span>
      </div>
    </div>
    <div class="extra content">
      <actor-link :actor="library.actor" />
    </div>
    <div class="ui bottom attached buttons">
      <button
        v-if="!library.follow"
        @click="follow()"
        :class="['ui', 'green', {'loading': isLoadingFollow}, 'button']">
        <translate>Follow</translate>
      </button>
      <button
        v-else-if="!library.follow.approved"
        class="ui disabled button"><i class="hourglass icon"></i>
        <translate>Follow pending approval</translate>
      </button>
      <button
        v-else-if="!library.follow.approved"
        class="ui disabled button"><i class="check icon"></i>
        <translate>Following</translate>
      </button>
      <dangerous-button
        v-else-if="library.follow.approved"
        color=""
        :class="['ui', 'button']"
        :action="unfollow">
        <translate>Unfollow</translate>
        <p slot="modal-header"><translate>Unfollow this library?</translate></p>
        <div slot="modal-content">
          <p><translate>By unfollowing this library, you will loose access to its content.</translate></p>
        </div>
        <p slot="modal-confirm"><translate>Unfollow</translate></p>
      </dangerous-button>
    </div>
  </div>
</template>
<script>
import axios from 'axios'

export default {
  props: ['library'],
  data () {
    return {
      isLoadingFollow: false,
      showScan: false,
      scanTimeout: null,
      latestScan: this.library.latest_scan,
    }
  },
  computed: {
    labels () {
      let me = this.$gettext('This library is private and you will need approval from its owner to access its content')
      let everyone = this.$gettext('This library is public and you can access its content without any authorization')

      return {
        tooltips: {
          me,
          everyone
        }
      }
    },
    scanProgress () {
      let scan = this.latestScan
      let progress = scan.processed_files * 100 / scan.total_files
      return Math.min(parseInt(progress), 100)
    },
    scanStatus () {
      if (this.latestScan) {
        return this.latestScan.status
      }
      return 'unknown'
    },
    canLaunchScan () {
      if (this.scanStatus === 'pending') {
        return false
      }
      if (this.scanStatus === 'scanning') {
        return false
      }
      return true
    }
  },
  methods: {
    launchScan () {
      let self = this
      let successMsg = this.$gettext('Scan launched')
      let skippedMsg = this.$gettext('Scan skipped (previous scan is too recent)')
      axios.post(`federation/libraries/${this.library.uuid}/scan/`).then((response) => {
        let msg
        if (response.data.status == 'skipped') {
          msg = skippedMsg
        } else {
          self.latestScan = response.data.scan
          msg = successMsg
        }
        self.$store.commit('ui/addMessage', {
          content: msg,
          date: new Date()
        })
      })
    },
    follow () {
      let self = this
      this.isLoadingFollow = true
      axios.post('federation/follows/library/', {target: this.library.uuid}).then((response) => {
        self.library.follow = response.data
        self.isLoadingFollow = false
        self.$emit('followed')

      }, error => {
        self.isLoadingFollow = false
      })
    },
    unfollow () {
      let self = this
      this.isLoadingFollow = true
      axios.delete(`federation/follows/library/${this.library.follow.uuid}/`).then((response) => {
        self.$emit('deleted')
        self.isLoadingFollow = false
      }, error => {
        self.isLoadingFollow = false
      })
    },
    fetchScanStatus () {
      let self = this
      axios.get(`federation/follows/library/${this.library.follow.uuid}/`).then((response) => {
        self.latestScan = response.data.target.latest_scan
        if (self.scanStatus === 'pending' || self.scanStatus === 'scanning') {
          self.scanTimeout = setTimeout(self.fetchScanStatus(), 5000)
        } else {
          clearTimeout(self.scanTimeout)
        }
      })
    }
  },
  watch: {
    showScan (newValue, oldValue) {
      if (newValue) {
        if (this.scanStatus === 'pending' || this.scanStatus === 'scanning') {
          this.fetchScanStatus()
        }
      } else {
        if (this.scanTimeout) {
          clearTimeout(this.scanTimeout)
        }
      }
    }
  }
}
</script>
