<template>
  <main class="main pusher" v-title="labels.title">
    <section class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
            <translate translate-context="Content/About/Title/Short, Noun" v-if="instance.name.value" :translate-params="{instance: instance.name.value}">
             About %{ instance }
            </translate>
            <translate translate-context="Content/About/Title/Short, Noun" v-else>About this instance</translate>
        </h1>
        <stats></stats>
      </div>
    </section>
    <section class="ui vertical stripe segment">
      <div
        class="ui middle aligned stackable text container">
        <p
        v-if="!instance.short_description.value && !instance.long_description.value"><translate translate-context="Content/About/Paragraph">Unfortunately, the owners of this instance did not yet take the time to complete this page.</translate></p>
        <router-link
          class="ui button"
          v-if="$store.state.auth.availablePermissions['settings']"
          :to="{path: '/manage/settings', hash: 'instance'}">
          <i class="pencil icon"></i><translate translate-context="Content/Settings/Button.Label/Verb">Edit instance info</translate>
        </router-link>
        <div class="ui hidden divider"></div>
      </div>
      <div
        v-if="instance.short_description.value"
        class="ui middle aligned stackable text container">
        <p>{{ instance.short_description.value }}</p>
      </div>
      <div
        v-if="markdown && instance.long_description.value"
        class="ui middle aligned stackable text container"
        v-html="markdown.makeHtml(instance.long_description.value)">
      </div>
    </section>
  </main>
</template>

<script>
import { mapState } from "vuex"
import Stats from "@/components/instance/Stats"

export default {
  components: {
    Stats
  },
  data () {
    return {
      markdown: null
    }
  },
  created () {
    this.$store.dispatch("instance/fetchSettings")
    let self = this
    import('showdown').then(module => {
      self.markdown = new module.default.Converter()
    })
  },
  computed: {
    ...mapState({
      instance: state => state.instance.settings.instance
    }),
    labels() {
      return {
        title: this.$pgettext('Head/About/Title', "About this instance")
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
