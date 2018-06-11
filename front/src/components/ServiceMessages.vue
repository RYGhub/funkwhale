<template>
  <div class="service-messages">
    <message v-for="message in displayedMessages" :key="String(message.date)" :class="['large', getLevel(message)]">
      <p>{{ message.content }}</p>
    </message>
  </div>
</template>

<script>
import {mapState} from 'vuex'

export default {
  data () {
    return {
      date: new Date(),
      interval: null
    }
  },
  created () {
    this.setupInterval()
  },
  destroyed () {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },
  computed: {
    ...mapState({
      messages: state => state.ui.messages,
      displayDuration: state => state.ui.messageDisplayDuration
    }),
    displayedMessages () {
      let now = this.date
      let interval = this.displayDuration
      let toDisplay = this.messages.filter(m => {
        return now - m.date <= interval
      })
      return toDisplay.slice(0, 3)
    }
  },
  methods: {
    setupInterval () {
      if (this.interval) {
        return
      }
      let self = this
      this.interval = setInterval(() => {
        if (self.displayedMessages.length === 0) {
          clearInterval(self.interval)
          this.interval = null
        }
        self.date = new Date()
      }, 1000)
    },
    getLevel (message) {
      return message.level || 'info'
    }
  },
  watch: {
    messages: {
      handler (v) {
        if (v.length > 0 && !this.interval) {
          this.setupInterval()
        }
      },
      deep: true
    }
  }
}
</script>

<style>
.service-messages {
  z-index: 9999;
  margin-left: 1em;
  min-width: 20em;
  max-width: 40em;
}
.service-messages .message:last-child {
  margin-bottom: 0;
}
</style>
