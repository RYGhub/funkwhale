<template>
  <tr :class="[{'disabled-row': item.is_read}]">
    <td>
      <actor-link class="user" :actor="item.activity.actor" />
    </td>
    <td>
      <router-link tag="span" class="link" v-if="notificationData.detailUrl" :to="notificationData.detailUrl">
        {{ notificationData.message }}
      </router-link>
      <template v-else>{{ notificationData.message }}</template>
      <template v-if="notificationData.action">&nbsp;
        <div @click="handleAction(notificationData.action.handler)" :class="['ui', 'basic', 'tiny', notificationData.action.buttonClass || '', 'button']">
          <i v-if="notificationData.action.icon" :class="[notificationData.action.icon, 'icon']" />
          {{ notificationData.action.label }}
        </div>
      </template>
    </td>
    <td><human-date :date="item.activity.creation_date" /></td>
    <td class="read collapsing">
      <span @click="markRead(false)" v-if="item.is_read" :title="labels.markUnread">
        <i class="redo icon" />
      </span>
      <span @click="markRead(true)" v-else :title="labels.markRead">
        <i class="check icon" />
      </span>
    </td>
  </tr>
</template>
<script>
import axios from 'axios'

export default {
  props: ['item'],
  computed: {
    message () {
      return 'plop'
    },
    labels () {
      let libraryFollowMessage = this.$gettext('%{ username } followed your library "%{ library }"')
      let libraryAcceptFollowMessage = this.$gettext('%{ username } accepted your follow on library "%{ library }"')
      return {
        libraryFollowMessage,
        libraryAcceptFollowMessage,
        markRead: this.$gettext('Mark as read'),
        markUnread: this.$gettext('Mark as unread'),

      }
    },
    username () {
      return this.item.activity.actor.preferred_username
    },
    notificationData () {
      let self = this
      let a = this.item.activity
      if (a.type === 'Follow') {
        if (a.object && a.object.type === 'music.Library') {
          let action = null
          if (!a.related_object.approved) {
            action = {
              buttonClass: 'green',
              icon: 'check',
              label: this.$gettext('Approve'),
              handler: () => { self.approveLibraryFollow(a.related_object) }
            }
          }
          return {
            action,
            detailUrl: {name: 'content.libraries.detail', params: {id: a.object.uuid}},
            message: this.$gettextInterpolate(
              this.labels.libraryFollowMessage,
              {username: this.username, library: a.object.name}
            )
          }
        }
      }
      if (a.type === 'Accept') {
        if (a.object && a.object.type === 'federation.LibraryFollow') {
          return {
            detailUrl: {name: 'content.remote.index'},
            message: this.$gettextInterpolate(
              this.labels.libraryAcceptFollowMessage,
              {username: this.username, library: a.related_object.name}
            )
          }
        }
      }
      return {}
    }
  },
  methods: {
    handleAction (handler) {
      // call handler then mark notification as read
      handler()
      this.markRead(true)
    },
    approveLibraryFollow (follow) {
      let self = this
      let action = 'accept'
      axios.post(`federation/follows/library/${follow.uuid}/${action}/`).then((response) => {
        follow.isLoading = false
        follow.approved = true
      })
    },
    markRead (value) {
      let self = this
      let action = 'accept'
      axios.patch(`federation/inbox/${this.item.id}/`, {is_read: value}).then((response) => {
        self.item.is_read = value
        if (value) {
          self.$store.commit('ui/incrementNotifications', {type: 'inbox', count: -1})
        } else {
          self.$store.commit('ui/incrementNotifications', {type: 'inbox', count: 1})
        }
      })
    }
  }
}
</script>
<style scoped>
.read > span {
  cursor: pointer;
}
.disabled-row {
  color: rgba(40, 40, 40, 0.3);
}
</style>
