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
      <div class="content">
        <i class="music icon"></i>
        <translate :translate-params="{count: library.files_count}" :translate-n="library.files_count" translate-plural="%{ count } tracks">1 tracks</translate>
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
      <button
        v-else-if="library.follow.approved"
        class="ui button"><i class="x icon"></i>
        <translate>Unfollow</translate>
      </button>
    </div>
  </div>
</template>
<script>
import axios from 'axios'

export default {
  props: ['library'],
  data () {
    return {
      isLoadingFollow: false
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
    }
  },
  methods: {
    follow () {
      let self = this
      this.isLoadingFollow = true
      axios.post('federation/follows/library/', {target: this.library.uuid}).then((response) => {
        self.library.follow = response.data
        self.isLoadingFollow = false
      }, error => {
        self.isLoadingFollow = false
      })
    }
  }
}
</script>
