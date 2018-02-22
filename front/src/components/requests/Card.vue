<template>
  <div :class="['ui', {collapsed: collapsed}, 'card']">
    <div class="content">
      <div class="header">{{ request.artist_name }}</div>
      <div class="description">
        <div
          v-if="request.albums" v-html="$options.filters.markdown(request.albums)"></div>
        <div v-if="request.comment" class="ui comments">
          <comment
            :user="request.user"
            :content="request.comment"
            :date="request.creation_date"></comment>
        </div>
      </div>
    </div>
    <div class="extra content">
      <span >
        <i v-if="request.status === 'pending'" class="hourglass start icon"></i>
        <i v-if="request.status === 'accepted'" class="hourglass half icon"></i>
        <i v-if="request.status === 'imported'" class="check icon"></i>
        {{ request.status | capitalize }}
      </span>
      <button
        @click="createImport"
        v-if="request.status === 'pending' && importAction && $store.state.auth.availablePermissions['import.launch']"
        class="ui mini basic green right floated button">Create import</button>
      
    </div>
  </div>
</template>

<script>
import Comment from '@/components/discussion/Comment'

export default {
  props: {
    request: {type: Object, required: true},
    importAction: {type: Boolean, default: true}
  },
  components: {
    Comment
  },
  data () {
    return {
      collapsed: true
    }
  },
  methods: {
    createImport () {
      this.$router.push({
        name: 'library.import.launch',
        query: {request: this.request.id}})
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
