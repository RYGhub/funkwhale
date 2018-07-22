<template>
  <div class="event">
   <div class="label">
     <i class="pink heart icon"></i>
   </div>
   <div class="content">
     <div class="summary">
       <translate :translate-params="{user: event.actor.local_id}">%{ user } favorited a track</translate>
       <human-date class="date" :date="event.published" />
     </div>
     <div class="extra text">
       <router-link :to="{name: 'library.tracks.detail', params: {id: event.object.local_id }}">{{ event.object.name }}</router-link>
       <translate :translate-params="{album: event.object.album, artist: event.object.artist}">from %{ album } by %{ artist }</translate>
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
