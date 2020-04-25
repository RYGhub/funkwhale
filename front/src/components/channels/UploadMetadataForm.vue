<template>
  <div :class="['ui', {loading: isLoading}, 'form']">
    <div class="ui required field">
      <label for="upload-title">
        <translate translate-context="*/*/*/Noun">Title</translate>
      </label>
      <input type="text" v-model="newValues.title">
    </div>
    <attachment-input
      v-model="newValues.cover"
      :required="false"
      @delete="newValues.cover = null">
      <translate translate-context="Content/Channel/*" slot="label">Track Picture</translate>
    </attachment-input>
    <div class="ui small hidden divider"></div>
    <div class="ui two fields">
      <div class="ui field">
        <label for="upload-tags">
          <translate translate-context="*/*/*/Noun">Tags</translate>
        </label>
        <tags-selector
          v-model="newValues.tags"
          id="upload-tags"
          :required="false"></tags-selector>
      </div>
      <div class="ui field">
        <label for="upload-position">
          <translate translate-context="*/*/*/Short, Noun">Position</translate>
        </label>
        <input type="number" min="1" step="1" v-model="newValues.position">
      </div>
    </div>
    <div class="ui field">
      <label for="upload-description">
        <translate translate-context="*/*/*">Description</translate>
      </label>
      <content-form v-model="newValues.description" field-id="upload-description"></content-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import TagsSelector from '@/components/library/TagsSelector'
import AttachmentInput from '@/components/common/AttachmentInput'

export default {
  props: ['upload', 'values'],
  components: {
    TagsSelector,
    AttachmentInput
  },
  data () {
    return {
      newValues: {...this.values} || this.upload.import_metadata
    }
  },
  computed: {
    isLoading ()  {
      return !!this.metadata
    }
  },
  watch: {
    newValues: {
      handler (v) {
        this.$emit('values', v)
      },
      immediate: true
    },
  }
}
</script>
