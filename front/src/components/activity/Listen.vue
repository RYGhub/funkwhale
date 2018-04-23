<template>
  <div class="event">
   <div class="label">
     <i class="orange sound icon"></i>
   </div>
   <div class="content">
     <div class="summary">
       <i18next path="{%0%} listened to a track">
         <username class="user" :username="event.actor.local_id" />
       </i18next>
       <human-date class="date" :date="event.published" />

     </div>
     <div class="extra text">
       <router-link :to="{name: 'library.tracks.detail', params: {id: event.object.local_id }}">{{ event.object.name }}</router-link>
        <i18next path="from album {%0%}, by {%1%}" v-if="event.object.album">
          {{ event.object.album }}<em>{{ event.object.artist }}</em>
        </i18next>
        <i18next path=", by {%0%}" v-else>
          <em>{{ event.object.artist }}</em>
        </i18next>
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
