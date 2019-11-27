<template>
  <div>
    <div v-if="errors.length > 0" class="ui negative message">
      <div class="header"><translate translate-context="Content/*/Error message.Title">Your attachment cannot be saved</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>
    <div class="ui stackable two column grid">
      <div class="column" v-if="value && value === initialValue">
        <h3 class="ui header"><translate translate-context="Content/*/Title/Noun">Current file</translate></h3>
        <img class="ui image" v-if="value" :src="$store.getters['instance/absoluteUrl'](`api/v1/attachments/${value}/proxy?next=medium_square_crop`)" />
      </div>
      <div class="column" v-else-if="attachment">
        <h3 class="ui header"><translate translate-context="Content/*/Title/Noun">New file</translate></h3>
        <img class="ui image" v-if="attachment && attachment.square_crop" :src="$store.getters['instance/absoluteUrl'](attachment.medium_square_crop)" />
      </div>
      <div class="column" v-if="!attachment">
        <div class="ui basic segment">
          <h3 class="ui header"><translate translate-context="Content/*/Title/Noun">New file</translate></h3>
          <p><translate translate-context="Content/*/Paragraph">PNG or JPG. At most 5MB. Will be downscaled to 400x400px.</translate></p>
          <input class="ui input" ref="attachment" type="file" accept="image/x-png,image/jpeg" @change="submit" />
          <div v-if="isLoading" class="ui active inverted dimmer">
            <div class="ui indeterminate text loader">
              <translate translate-context="Content/*/*/Noun">Uploading file…</translate>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
<script>
import axios from 'axios'

export default {
  props: ['value', 'initialValue'],
  data () {
    return {
      attachment: null,
      isLoading: false,
      errors: [],
    }
  },
  methods: {
    submit() {
      this.isLoading = true
      this.errors = []
      let self = this
      this.file = this.$refs.attachment.files[0]
      let formData = new FormData()
      formData.append("file", this.file)
      axios
        .post(`attachments/`, formData, {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        })
        .then(
          response => {
            this.isLoading = false
            self.attachment = response.data
            self.$emit('input', self.attachment.uuid)
          },
          error => {
            self.isLoading = false
            self.errors = error.backendErrors
          }
        )
    },
    remove() {
      this.isLoading = true
      this.errors = []
      let self = this
      axios.delete(`attachments/${this.attachment.uuid}/`)
        .then(
          response => {
            this.isLoading = false
            self.attachment = null
            self.$emit('delete')
          },
          error => {
            self.isLoading = false
            self.errors = error.backendErrors
          }
        )
    },
  },
  watch: {
    value (v) {
      if (this.attachment && v === this.initialValue) {
        // we had a reset to initial value
        this.remove()
      }
    }
  }
}
</script>
