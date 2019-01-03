<script>

import {normalizeQuery, parseTokens, compileTokens} from '@/search'

export default {
  props: {
    defaultQuery: {type: String, required: false},
    updateUrl: {type: Boolean, required: false, default: false},
  },
  methods: {
    getTokenValue (key, fallback) {
      let matching = this.search.tokens.filter(t => {
        return t.field === key
      })
      if (matching.length > 0) {
        return matching[0].value
      }
      return fallback
    },
    addSearchToken (key, value) {
      if (!value) {
        // we remove existing matching tokens, if any
        this.search.tokens = this.search.tokens.filter(t => {
          return t.field != key
        })
      } else {
        let existing = this.search.tokens.filter(t => {
          return t.field === key
        })
        if (existing.length > 0) {
          // we replace the value in existing tokens, if any
          existing.forEach(t => {
            t.value = value
          })
        } else {
          // we add a new token
          this.search.tokens.push({field: key, value})
        }
      }
    },
  },
  watch: {
    'search.query' (newValue) {
      this.search.tokens = parseTokens(normalizeQuery(newValue))
    },
    'search.tokens': {
      handler (newValue) {
        this.search.query = compileTokens(newValue)
        this.page = 1
        this.fetchData()
        if (this.updateUrl) {
          let params = {}
          if (this.search.query) {
            params.q = this.search.query
          }
          this.$router.replace({
            query: params
          })
        }
      },
      deep: true
    },
  }
}
</script>
