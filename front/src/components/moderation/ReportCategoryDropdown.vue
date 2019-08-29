<template>
  <div>
    <label v-if="label"><translate translate-context="*/*/*">Category</translate></label>
    <select class="ui dropdown" :value="value" @change="$emit('input', $event.target.value)">
      <option :value="option.value" v-for="option in allCategories">{{ option.label }}</option>
    </select>
  </div>
</template>

<script>
import TranslationsMixin from '@/components/mixins/Translations'
import lodash from '@/lodash'
export default {
  mixins: [TranslationsMixin],
  props: ['value', 'all', 'label'],
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
      return c.concat(
        lodash.keys(this.sharedLabels.fields.report_type.choices).sort().map((v) => {
          return {
            value: v,
            label: this.sharedLabels.fields.report_type.choices[v]
          }
        })
      )
    }
  }
}
</script>
