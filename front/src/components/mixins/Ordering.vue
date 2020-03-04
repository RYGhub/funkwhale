<script>
export default {
  props: {
    defaultOrdering: {type: String, required: false},
    orderingConfigName: {type: String, required: false},
  },
  computed: {
    orderingConfig () {
      return this.$store.state.ui.routePreferences[this.orderingConfigName || this.$route.name]
    },
    paginateBy: {
      set(paginateBy) {
        this.$store.commit('ui/paginateBy', {
          route: this.$route.name,
          value: paginateBy
        })
      },
      get() {
        return this.orderingConfig.paginateBy
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
        return this.orderingConfig.ordering
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
        return this.orderingConfig.orderingDirection
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
