<script>
export default {
  props: {
    defaultOrdering: {type: String, required: false}
  },
  methods: {
    getOrderingFromString (s) {
      let parts = s.split('-')
      if (parts.length > 1) {
        return {
          direction: '-',
          field: parts.slice(1).join('-')
        }
      } else {
        return {
          direction: '',
          field: s
        }
      }
    },
    getOrderingAsString () {
      return [this.orderingDirection, this.ordering].join('')
    }
  }
}
</script>
