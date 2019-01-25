<template>
  <footer id="footer" role="contentinfo" class="ui vertical footer segment">
    <div class="ui container">
      <div class="ui stackable equal height stackable grid">
        <section class="four wide column">
          <h4 v-translate class="ui header">
            <translate :translate-params="{instanceName: instanceHostname}" >About %{instanceName}</translate>
          </h4>
          <div class="ui link list">
            <router-link class="item" to="/about">
              <translate>About page</translate>
            </router-link>
            <div class="item" v-if="version">
              <translate :translate-params="{version: version}" >Version %{version}</translate>
            </div>
            <a @click="switchInstance" class="item" >
              <translate>Use another instance</translate>
            </a>
          </div>
          <div class="ui form">
            <div class="ui field">
              <label><translate>Change language</translate></label>
              <select class="ui dropdown" :value="$language.current" @change="$store.commit('ui/currentLanguage', $event.target.value)">
                <option v-for="(language, key) in $language.available" :key="key" :value="key">{{ language }}</option>
              </select>
            </div>
          </div>
        </section>
        <section class="four wide column">
          <h4 v-translate class="ui header">Using Funkwhale</h4>
          <div class="ui link list">
            <a href="https://docs.funkwhale.audio" class="item" target="_blank"><translate>Documentation</translate></a>
            <a href="https://docs.funkwhale.audio/users/apps.html" class="item" target="_blank"><translate>Mobile and desktop apps</translate></a>
            <div role="button" class="item" @click="$emit('show:shortcuts-modal')"><translate>Keyboard shortcuts</translate></div>
          </div>
        </section>
        <section class="four wide column">
          <h4 v-translate class="ui header">Getting help</h4>
          <div class="ui link list">
            <a href="https://socialhub.network/c/funkwhale" class="item" target="_blank"><translate>Support forum</translate></a>
            <a href="https://riot.im/app/#/room/#funkwhale-troubleshooting:matrix.org" class="item" target="_blank"><translate>Chat room</translate></a>
            <a href="https://dev.funkwhale.audio/funkwhale/funkwhale/issues" class="item" target="_blank"><translate>Issue tracker</translate></a>
          </div>
        </section>
        <section class="four wide column">
          <h4 v-translate class="ui header">About Funkwhale</h4>
          <div class="ui link list">
            <a href="https://funkwhale.audio" class="item" target="_blank"><translate>Official website</translate></a>
            <a href="https://contribute.funkwhale.audio" class="item" target="_blank"><translate>Contribute</translate></a>
            <a href="https://dev.funkwhale.audio/funkwhale/funkwhale" class="item" target="_blank"><translate>Source code</translate></a>
          </div>
          <div class="ui hidden divider"></div>
          <p>
            <translate>The funkwhale logo was kindly designed and provided by Francis Gading.</translate>
          </p>
        </section>
      </div>
    </div>
  </footer>
</template>

<script>
import Vue from "vue"
import { mapState } from "vuex"
import axios from 'axios'

export default {
  props: ["version"],
  methods: {
    switchInstance() {
      let confirm = window.confirm(
        this.$gettext(
          "This will erase your local data and disconnect you, do you want to continue?"
        )
      )
      if (confirm) {
        this.$store.commit("instance/instanceUrl", null)
      }
    }
  },
  computed: {
    ...mapState({
      messages: state => state.ui.messages
    }),
    instanceHostname() {
      let url = this.$store.state.instance.instanceUrl
      let parser = document.createElement("a")
      parser.href = url
      return parser.hostname
    },
    suggestedInstances() {
      let instances = [
        this.$store.getters["instance/defaultUrl"](),
        "https://demo.funkwhale.audio"
      ]
      return instances
    }
  }
}
</script>
<style scoped>
footer p {
  color: grey;
}
</style>
