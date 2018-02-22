<template>
  <div class="comment">
    <div class="content">
      <a class="author">{{ user.username }}</a>
      <div class="metadata">
        <div class="date">{{ date | ago }}</div>
      </div>
      <div class="text" v-html="comment"></div>
      </div>
      <div class="actions">
        <span
          @click="collapsed = false"
          v-if="truncated && collapsed"
          class="expand">Expand</span>
        <span
          @click="collapsed = true"
          v-if="truncated && !collapsed"
          class="collapse">Collapse</span>
      </div>
    </div>
  </div>
</template>
<script>
  export default {
    props: {
      user: {type: Object, required: true},
      date: {required: true},
      content: {type: String, required: true}
    },
    data () {
      return {
        collapsed: true,
        length: 50
      }
    },
    computed: {
      comment () {
        let text = this.content
        if (this.collapsed) {
          text = this.$options.filters.truncate(text, this.length)
        }
        return this.$options.filters.markdown(text)
      },
      truncated () {
        return this.content.length > this.length
      }
    }
  }
</script>
