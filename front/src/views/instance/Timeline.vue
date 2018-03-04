<template>
  <div class="main pusher">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui header">Recent activity on this instance</h1>
        <div class="ui feed">
          <component
            class="event"
            v-for="(event, index) in events"
            :key="event.id + index"
            v-if="components[event.type]"
            :is="components[event.type]"
            :event="event">
            <username
              class="user"
              :username="event.actor.local_id"
              slot="user"></username>
              {{ event.published }}
            <human-date class="date" :date="event.published" slot="date"></human-date>
          </component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'

import Like from '@/components/activity/Like'
import Listen from '@/components/activity/Listen'

export default {
  data () {
    return {
      components: {
        'Like': Like,
        'Listen': Listen
      }
    }
  },
  computed: {
    ...mapState({
      events: state => state.instance.events
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
