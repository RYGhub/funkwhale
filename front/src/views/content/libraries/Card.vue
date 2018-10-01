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
        <i class="music icon"></i> {{ library.uploads_count }}
        <translate :translate-params="{count: library.uploads_count}" :translate-n="library.uploads_count" translate-plural="%{ count } tracks">1 track</translate>
      </div>
    </div>
    <div class="ui bottom basic attached buttons">
      <router-link :to="{name: 'content.libraries.detail.upload', params: {id: library.uuid}}" class="ui button">
        <translate>Upload</translate>
      </router-link>
      <router-link :to="{name: 'content.libraries.detail', params: {id: library.uuid}}" exact class="ui button">
        <translate>Detail</translate>
      </router-link>
    </div>
  </div>
</template>
<script>
export default {
  props: ['library'],
  computed: {
    labels () {
      let me = this.$gettext('Visibility: nobody except me')
      let instance = this.$gettext('Visibility: everyone on this instance')
      let everyone = this.$gettext('Visibility: everyone, including other instances')
      let size = this.$gettext('Total size of the files in this library')

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
