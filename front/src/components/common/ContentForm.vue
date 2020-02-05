<template>
  <div class="content-form ui segments">
    <div class="ui segment">
      <div class="ui tiny secondary pointing menu">
        <button @click.prevent="isPreviewing = false" :class="[{active: !isPreviewing}, 'item']">
          <translate translate-context="*/Form/Menu.item">Write</translate>
        </button>
        <button @click.prevent="isPreviewing = true" :class="[{active: isPreviewing}, 'item']">
          <translate translate-context="*/Form/Menu.item">Preview</translate>
        </button>
      </div>
      <template v-if="isPreviewing" >

        <div class="ui placeholder" v-if="isLoadingPreview">
          <div class="paragraph">
            <div class="line"></div>
            <div class="line"></div>
            <div class="line"></div>
            <div class="line"></div>
          </div>
        </div>
        <p v-else-if="preview === null">
          <translate translate-context="*/Form/Paragraph">Nothing to preview.</translate>
        </p>
        <div v-html="preview" v-else></div>
      </template>
      <template v-else>
        <div class="ui transparent input">
          <textarea ref="textarea" :name="fieldId" :id="fieldId" rows="5" v-model="newValue" :placeholder="labels.placeholder"></textarea>
        </div>
        <div class="ui very small hidden divider"></div>
      </template>
    </div>
    <div class="ui bottom attached segment">
      <span :class="['right', 'floated', {'ui red text': remainingChars < 0}]">
        {{ remainingChars }}
      </span>
      <p>
        <translate translate-context="*/Form/Paragraph">Markdown syntax is supported.</translate>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    value: {type: String, default: ""},
    fieldId: {type: String, default: "change-content"},
    autofocus: {type: Boolean, default: false},
  },
  data () {
    return {
      isPreviewing: false,
      preview: null,
      newValue: this.value,
      isLoadingPreview: false,
      charLimit: 5000,
    }
  },
  mounted () {
    if (this.autofocus) {
      this.$nextTick(() => {
        this.$refs.textarea.focus()
      })
    }
  },
  methods: {
    async loadPreview () {
      this.isLoadingPreview = true
      try {
        let response = await axios.post('text-preview/', {text: this.value})
        this.preview = response.data.rendered
      } catch {

      }
      this.isLoadingPreview = false
    }
  },
  computed: {
    labels () {
      return {
        placeholder: this.$pgettext("*/Form/Placeholder", "Write a few words here…")
      }
    },
    remainingChars () {
      return this.charLimit - this.value.length
    }
  },
  watch: {
    newValue (v) {
      this.$emit('input', v)
    },
    value: {
      async handler (v) {
        this.preview = null
        this.newValue = v
        if (this.isPreviewing) {
          await this.loadPreview()
        }
      },
      immediate: true,
    },
    async isPreviewing (v) {
      if (v && !!this.value && this.preview === null) {
        await this.loadPreview()
      }
      if (!v) {
        this.$nextTick(() => {
          this.$refs.textarea.focus()
        })
      }
    }
  }
}
</script>
