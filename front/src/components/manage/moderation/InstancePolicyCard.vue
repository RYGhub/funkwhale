<template>
  <div>
    <slot></slot>
    <p>
      <i class="clock outline icon"></i><human-date :date="object.creation_date" /> &nbsp;
      <i class="user icon"></i>{{ object.actor }}  &nbsp;
      <template v-if="object.is_active">
        <i class="play icon"></i>
        <translate>Enabled</translate>
      </template>
      <template v-if="!object.is_active">
        <i class="pause icon"></i>
        <translate>Paused</translate>
      </template>
    </p>
    <div>
      <p><strong><translate>Rule</translate></strong></p>
      <p v-if="object.block_all">
        <i class="ban icon"></i>
        <translate>Block everything</translate>
      </p>
      <div v-else class="ui list">
        <div class="ui item" v-if="object.silence_activity">
          <i class="feed icon"></i>
          <div class="content"><translate>Mute activity</translate></div>
        </div>
        <div class="ui item" v-if="object.silence_notifications">
          <i class="bell icon"></i>
          <div class="content"><translate>Mute notifications</translate></div>
        </div>
        <div class="ui item" v-if="object.reject_media">
          <i class="file icon"></i>
          <div class="content"><translate>Reject media</translate></div>
        </div>

      </div>
    </div>
    <div v-if="markdown && object.summary">
      <div class="ui hidden divider"></div>
      <p><strong><translate>Reason</translate></strong></p>
      <div v-html="markdown.makeHtml(object.summary)"></div>
    </div>
    <div class="ui hidden divider"></div>
    <button @click="$emit('update')" class="ui right floated labeled icon button">
      <i class="edit icon"></i>
      <translate>Update</translate>
    </button>
  </div>
</template>

<script>

export default {
  props: {
    object: {type: Object, default: null},
  },
  data () {
    return {
      markdown: null
    }
  },
  created () {
    let self = this
    import('showdown').then(module => {
      self.markdown = new module.default.Converter({simplifiedAutoLink: true, openLinksInNewWindow: true})
    })
  }
}
</script>

<style scoped>
</style>
