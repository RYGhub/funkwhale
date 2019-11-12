<script>
export default {
  props: {
    defaultOrdering: {type: String, required: false}
  },
  computed: {
    paginateBy: {
      set(paginateBy) {
        this.$store.commit('ui/paginateBy', {
          route: this.$route.name,
          value: paginateBy
        })
      },
      get() {
        return this.$store.state.ui.routePreferences[this.$route.name].paginateBy
      }
    },
    ordering: {
      set(ordering) {
        this.$store.commit('ui/ordering', {
          route: this.$route.name,
          value: ordering
        })
      },
      get() {
        return this.$store.state.ui.routePreferences[this.$route.name].ordering
      }
    },
    orderingDirection: {
      set(orderingDirection) {
        this.$store.commit('ui/orderingDirection', {
          route: this.$route.name,
          value: orderingDirection
        })
      },
      get() {
        return this.$store.state.ui.routePreferences[this.$route.name].orderingDirection
      }
    },
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
          direction: '+',
          field: s
        }
      }
    },
    getOrderingAsString () {
      let direction = this.orderingDirection
      if (direction === '+') {
        direction = ''
      }
      return [direction, this.ordering].join('')
    }
  }
}
</script>
