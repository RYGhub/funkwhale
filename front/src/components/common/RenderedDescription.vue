<template>
  <div>
    <div v-html="content.html" v-if="content && !isUpdating"></div>
    <p v-else-if="!isUpdating">
      <translate translate-context="*/*/Placeholder">No description available</translate>
    </p>
    <template v-if="!isUpdating && canUpdate && updateUrl">
      <div class="ui hidden divider"></div>
      <span role="button" @click="isUpdating = true">
        <i class="pencil icon"></i>
        <translate translate-context="Content/*/Button.Label/Verb">Edit</translate>
      </span>
    </template>
    <form v-if="isUpdating" class="ui form" @submit.prevent="submit()">
      <div v-if="errors.length > 0" class="ui negative message">
        <div class="header"><translate translate-context="Content/Channels/Error message.Title">Error while updating description</translate></div>
        <ul class="list">
          <li v-for="error in errors">{{ error }}</li>
        </ul>
      </div>
      <content-form v-model="newText" :autofocus="true"></content-form>
      <a @click.prevent="isUpdating = false" class="left floated">
        <translate translate-context="*/*/Button.Label/Verb">Cancel</translate>
      </a>
      <button :class="['ui', {'loading': isLoading}, 'right', 'floated', 'button']" type="submit" :disabled="isLoading">
        <translate translate-context="Content/Channels/Button.Label/Verb">Update description</translate>
      </button>
      <div class="ui clearing hidden divider"></div>
    </form>
  </div>
</template>

<script>
import {secondsToObject} from '@/filters'
import axios from 'axios'

export default {
  props: {
    content: {required: true},
    fieldName: {required: false, default: 'description'},
    updateUrl: {required: false, type: String},
    canUpdate: {required: false, default: true, type: Boolean},
  },
  data () {
    return {
      isUpdating: false,
      newText: (this.content || {text: ''}).text,
      errors: null,
      isLoading: false,
      errors: [],
    }
  },
  methods: {
    submit () {
      let self = this
      this.isLoading = true
      this.errors = []
      let payload = {}
      payload[this.fieldName] = null
      if (this.newText) {
        payload[this.fieldName] = {
          content_type: "text/markdown",
          text: this.newText,
        }
      }
      axios.patch(this.updateUrl, payload).then((response) => {
        self.$emit('updated', response.data)
        self.isLoading = false
        self.isUpdating = false
      }, error => {
        self.errors = error.backendErrors
        self.isLoading = false
      })
    },
  }
}
</script>
