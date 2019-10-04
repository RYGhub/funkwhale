<template>
  <div>
    <label v-if="label"><translate translate-context="*/*/*">Category</translate></label>
    <select class="ui dropdown" :value="value" @change="$emit('input', $event.target.value)" :required="required">
      <option v-if="empty" disabled value=''></option>
      <option :value="option.value" v-for="option in allCategories">{{ option.label }}</option>
    </select>
    <slot></slot>
  </div>
</template>

<script>
import TranslationsMixin from '@/components/mixins/Translations'
import lodash from '@/lodash'
export default {
  mixins: [TranslationsMixin],
  props: {
    value: {},
    all: {},
    label: {},
    empty: {},
    required: {},
    restrictTo: {default: () => { return [] }}
  },
  computed: {
    allCategories () {
      let c = []
      if (this.all) {
        c.push(
          {
            value: '',
            label: this.$pgettext('Content/*/Dropdown', 'All')
          },
        )
      }
      let choices
      if (this.restrictTo.length > 0)  {
        choices = this.restrictTo
      } else {
        choices = lodash.keys(this.sharedLabels.fields.report_type.choices)
      }
      return c.concat(
        choices.sort().map((v) => {
          return {
            value: v,
            label: this.sharedLabels.fields.report_type.choices[v] || v
          }
        })
      )
    }
  }
}
</script>
