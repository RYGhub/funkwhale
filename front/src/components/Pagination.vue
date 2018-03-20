<template>
  <div class="ui pagination borderless menu">
    <a
      v-if="current - 1 >= 1"
      @click="selectPage(current - 1)"
      :class="[{'disabled': current - 1 < 1}, 'item']"><i class="angle left icon"></i></a>
    <template>
      <a
        v-if="page !== 'skip'"
        v-for="page in pages"
        @click="selectPage(page)"
        :class="[{'active': page === current}, 'item']">
        {{ page }}
      </a>
      <a v-else class="disabled item">
        ...
      </a>
    </template>
    <a
      v-if="current + 1 <= maxPage"
      @click="selectPage(current + 1)"
      :class="[{'disabled': current + 1 > maxPage}, 'item']"><i class="angle right icon"></i></a>
  </div>
</template>

<script>
import _ from 'lodash'

export default {
  props: {
    current: {type: Number, default: 1},
    paginateBy: {type: Number, default: 25},
    total: {type: Number}
  },
  computed: {
    pages: function () {
      let range = 2
      let current = this.current
      let beginning = _.range(1, Math.min(this.maxPage, 1 + range))
      let middle = _.range(Math.max(1, current - range + 1), Math.min(this.maxPage, current + range))
      let end = _.range(this.maxPage, Math.max(1, this.maxPage - range))
      let allowed = beginning.concat(middle, end)
      allowed = _.uniq(allowed)
      allowed = _.sortBy(allowed, [(e) => { return e }])
      let final = []
      allowed.forEach(p => {
        let last = final.slice(-1)[0]
        let consecutive = true
        if (last === 'skip') {
          consecutive = false
        } else {
          if (!last) {
            consecutive = true
          } else {
            consecutive = last + 1 === p
          }
        }
        if (consecutive) {
          final.push(p)
        } else {
          if (p !== 'skip') {
            final.push('skip')
            final.push(p)
          }
        }
      })
      return final
    },
    maxPage: function () {
      return Math.ceil(this.total / this.paginateBy)
    }
  },
  methods: {
    selectPage: function (page) {
      if (this.current !== page) {
        this.$emit('page-changed', page)
      }
    }
  }
}
</script>

<style scoped>
.ui.menu {
  border: none;
  box-shadow: none;
}
</style>
