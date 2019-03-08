<template>
  <div class="ui card">
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
          v-else-if="library.privacy_level === 'instance'"
          class="right floated"
          :data-tooltip="labels.tooltips.instance">
          <i class="small circle outline icon"></i>
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
      <div class="description">
        <div class="ui hidden divider"></div>
      </div>
      <div class="content">
        <span v-if="library.size" class="right floated" :data-tooltip="labels.tooltips.size">
          <i class="database icon"></i>
          {{ library.size | humanSize }}
        </span>
        <i class="music icon"></i>
        <translate translate-context="Content/Library/Card.List item" :translate-params="{count: library.uploads_count}" :translate-n="library.uploads_count" translate-plural="%{ count } tracks">%{ count } track</translate>
      </div>
    </div>
    <div class="ui bottom basic attached buttons">
      <router-link :to="{name: 'content.libraries.detail.upload', params: {id: library.uuid}}" class="ui button">
        <translate translate-context="Content/Library/Card.Button.Label/Verb">Upload</translate>
      </router-link>
      <router-link :to="{name: 'content.libraries.detail', params: {id: library.uuid}}" exact class="ui button">
        <translate translate-context="Content/Library/Card.Button.Label/Noun">Details</translate>
      </router-link>
    </div>
  </div>
</template>
<script>
export default {
  props: ['library'],
  computed: {
    labels () {
      let me = this.$pgettext('Content/Library/Card.Help text', 'Visibility: nobody except me')
      let instance = this.$pgettext('Content/Library/Card.Help text', 'Visibility: everyone on this instance')
      let everyone = this.$pgettext('Content/Library/Card.Help text', 'Visibility: everyone, including other instances')
      let size = this.$pgettext('Content/Library/Card.Help text', 'Total size of the files in this library')

      return {
        tooltips: {
          me,
          instance,
          everyone,
          size
        }
      }
    }
  }
}
</script>
