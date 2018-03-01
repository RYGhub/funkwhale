<template>
  <div class="event">
   <div class="label">
     <i class="pink heart icon"></i>
   </div>
   <div class="content">
     <div class="summary">
       <slot name="user"></slot>
       favorited a track
       <slot name="date"></slot>
     </div>
     <div class="extra text">
       <router-link :to="{name: 'library.tracks.detail', params: {id: event.object.local_id }}">{{ event.object.name }}</router-link>
        <template v-if="event.object.album">from album {{ event.object.album }}, by <em>{{ event.object.artist }}</em>
        </template>
        <template v-else>, by <em>{{ event.object.artist }}</em>
        </template>

      </div>
   </div>
 </div>

</template>

<script>

export default {
  props: ['event']
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">

</style>
