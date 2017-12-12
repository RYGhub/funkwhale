<template>
  <div class="ui pagination borderless menu">
    <a
      @click="selectPage(1)"
      :class="[{'disabled': current === 1}, 'item']"><i class="angle double left icon"></i></a>
    <a
      @click="selectPage(current - 1)"
      :class="[{'disabled': current - 1 < 1}, 'item']"><i class="angle left icon"></i></a>
    <a
      v-for="page in pages"
      @click="selectPage(page)"
      :class="[{'active': page === current}, 'item']">
      {{ page }}
    </a>
    <a
      @click="selectPage(current + 1)"
      :class="[{'disabled': current + 1 > maxPage}, 'item']"><i class="angle right icon"></i></a>
      <a
        @click="selectPage(maxPage)"
        :class="[{'disabled': current === maxPage}, 'item']"><i class="angle double right icon"></i></a>
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
      return _.range(1, this.maxPage + 1)
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
</style>
