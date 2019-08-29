<template>
  <div class="ui feed">
    <div class="event" v-for="note in notes" :key="note.uuid">
      <div class="label">
        <i class="comment outline icon"></i>
      </div>
      <div class="content">
        <div class="summary">
          <actor-link :admin="true" :actor="note.author"></actor-link>
          <div class="date">
            <human-date :date="note.creation_date"></human-date>
          </div>
        </div>
        <div class="extra text">
          <expandable-div :content="note.summary">
            <div v-html="markdown.makeHtml(note.summary)"></div>
          </expandable-div>
        </div>
        <div class="meta">
          <a role="button" @click.prevent="remove(note)">
            <i class="trash icon"></i> <translate translate-context="*/*/*/Verb">Delete</translate>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import showdown from 'showdown'

export default {
  props: {
    notes: {required: true},
  },
  data () {
      return {
      markdown: new showdown.Converter(),
      isLoading: false,
    }
  },
  methods: {
    remove (obj) {
      let self = this
      this.isLoading = true
      axios.delete(`manage/moderation/notes/${obj.uuid}/`).then((response) => {
        self.$emit('deleted', obj.uuid)
        self.isLoading = false
      }, error => {
        self.isLoading = false
      })
    },
  }
}
</script>
