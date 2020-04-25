<template>
  <div>
    <label for="license-dropdown">
      <translate translate-context="Content/*/*/Noun">License</translate>
    </label>
    <select id="license-dropdown" :value="value" @input="$emit('input', $event.target.value)" class="ui search normal dropdown">
      <option value="">
        <translate translate-context="*/*/*">None</translate>
      </option>
      <option v-for="l in featuredLicenses" :key="l.code" :value="l.code">{{ l.name }}</option>
    </select>
    <p class="help" v-if="value">
      <div class="ui very small hidden divider"></div>
      <a :href="currentLicense.url"  v-if="value" target="_blank" rel="noreferrer noopener">
        <translate translate-context="Content/*/*">About this license</translate>
      </a>
    </p>
  </div>
</template>
<script>
import axios from 'axios'

export default {
  props: ['value'],
  data () {
    return {
      availableLicenses: [],
      featuredLicensesIds: [
        'cc0-1.0',
        'cc-by-4.0',
        'cc-by-sa-4.0',
        'cc-by-nc-4.0',
        'cc-by-nc-sa-4.0',
        'cc-by-nc-nd-4.0',
        'cc-by-nd-4.0',
      ],
      isLoading: false,
    }
  },
  async created () {
    await this.fetchLicenses()
  },
  computed: {
    featuredLicenses () {
      let self = this
      return this.availableLicenses.filter((l) => {
        return self.featuredLicensesIds.indexOf(l.code) > -1
      })
    },
    currentLicense () {
      let self = this
      if (this.value) {
        return this.availableLicenses.filter((l) => {
          return l.code === self.value
        })[0]

      }
    }
  },
  methods: {
    async fetchLicenses () {
      this.isLoading = true
      let response = await axios.get('licenses/')
      this.availableLicenses = response.data.results
      this.isLoading = false
    },
  },
}
</script>
