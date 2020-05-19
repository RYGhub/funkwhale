<template>
  <footer id="footer" role="contentinfo" class="ui vertical footer segment">
    <div class="ui container">
      <div class="ui stackable equal height stackable grid">
        <section class="four wide column">
          <h4 v-if="podName" class="ui header ellipsis">
            <translate translate-context="Footer/About/Title" :translate-params="{instanceName: podName}" >About %{instanceName}</translate>
          </h4>
          <h4 v-else class="ui header ellipsis">
            <translate translate-context="Footer/About/Title" :translate-params="{instanceUrl: instanceHostname}" >About %{instanceUrl}</translate>
          </h4>
          <div class="ui link list">
            <router-link class="item" to="/about">
              <translate translate-context="Footer/About/List item.Link">About page</translate>
            </router-link>
              <a v-if="version" class="item" href="https://github.com/Steffo99/funkwhale-ryg" target="_blank">
                <translate translate-context="Footer/*/List item" :translate-params="{version: version}" >funkwhale-ryg %{version}</translate>
              </a>
            <div role="button" class="item" @click="$emit('show:set-instance-modal')" >
              <translate translate-context="Footer/*/List item.Link">Use another instance</translate>
            </div>
          </div>
          <div class="ui form">
            <div class="ui field">
              <label><translate translate-context="Footer/Settings/Dropdown.Label/Short, Verb">Change language</translate></label>
              <select class="ui dropdown" :value="$language.current" @change="$store.commit('ui/currentLanguage', $event.target.value)">
                <option v-for="(language, key) in $language.available" :key="key" :value="key">{{ language }}</option>
              </select>
            </div>
          </div>
        </section>
        <section class="four wide column">
          <h4 v-translate class="ui header" translate-context="Footer/*/Title">Using Funkwhale</h4>
          <div class="ui link list">
            <a href="https://docs.funkwhale.audio" class="item" target="_blank"><translate translate-context="Footer/*/List item.Link/Short, Noun">Documentation</translate></a>
            <a href="https://funkwhale.audio/apps" class="item" target="_blank"><translate translate-context="Footer/*/List item.Link">Mobile and desktop apps</translate></a>
            <div role="button" class="item" @click="$emit('show:shortcuts-modal')"><translate translate-context="*/*/*/Noun">Keyboard shortcuts</translate></div>
          </div>
          <div class="ui form">
            <div class="ui field">
              <label><translate translate-context="Footer/Settings/Dropdown.Label/Short, Verb">Change theme</translate></label>
              <select class="ui dropdown" :value="$store.state.ui.theme" @change="$store.commit('ui/theme', $event.target.value)">
                <option v-for="theme in themes" :key="theme.key" :value="theme.key">{{ theme.name }}</option>
              </select>
            </div>
          </div>
        </section>
        <section class="four wide column">
          <h4 v-translate translate-context="Footer/*/Link" class="ui header">Royal Games</h4>
          <div class="ui link list">
            <a href="https://ryg.steffo.eu" class="item" target="_blank">Sito</a>
            <a href="https://discord.gg/UpuU9Y4" class="item" target="_blank">Discord</a>
            <a href="https://combo.steffo.eu" class="item" target="_blank">Files</a>
          </div>
        </section>
      </div>
    </div>
  </footer>
</template>

<script>
import Vue from "vue"
import { mapState } from "vuex"
import axios from 'axios'
import _ from '@/lodash'

export default {
  props: ["version"],
  computed: {
    ...mapState({
      messages: state => state.ui.messages,
      nodeinfo: state => state.instance.nodeinfo,
    }),
    podName() {
      return _.get(this.nodeinfo, 'metadata.nodeName')
    },
    instanceHostname() {
      let url = this.$store.state.instance.instanceUrl
      let parser = document.createElement("a")
      parser.href = url
      return parser.hostname
    },
    themes () {
      return [
        {
          name: this.$pgettext('Footer/Settings/Dropdown.Label/Theme name', 'Light'),
          key: 'light'
        },
        {
          name: this.$pgettext('Footer/Settings/Dropdown.Label/Theme name', 'Dark'),
          key: 'dark'
        }
      ]
    }
  }
}
</script>
