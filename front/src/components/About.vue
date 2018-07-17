<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
            <translate v-if="instance.name.value" :translate-params="{instance: instance.name.value}">
             About %{ instance }
            </translate>
            <translate v-else>About this instance</translate>
        </h1>
        <stats></stats>
      </div>
    </div>
    <div class="ui vertical stripe segment">
      <p v-if="!instance.short_description.value && !instance.long_description.value">
        <translate>Unfortunately, owners of this instance did not yet take the time to complete this page.</translate>
      </p>
      <router-link
        class="ui button"
        v-if="$store.state.auth.availablePermissions['settings']"
        :to="{path: '/manage/settings', hash: 'instance'}">
        <i class="pencil icon"></i><translate>Edit instance info</translate>
      </router-link>
      <div
        v-if="instance.short_description.value"
        class="ui middle aligned stackable text container">
        <p>{{ instance.short_description.value }}</p>
      </div>
      <div
        v-if="instance.long_description.value"
        class="ui middle aligned stackable text container"
        v-html="$options.filters.markdown(instance.long_description.value)">
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import Stats from '@/components/instance/Stats'

export default {
  components: {
    Stats
  },
  created () {
    this.$store.dispatch('instance/fetchSettings')
  },
  computed: {
    ...mapState({
      instance: state => state.instance.settings.instance
    }),
    labels () {
      return {
        title: this.$gettext('About this instance')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
