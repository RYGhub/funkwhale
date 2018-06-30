<template>
  <div class="ui card">
    <div class="content">
      <div v-if="isLoading" class="ui vertical segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <template v-if="data.id">
        <div class="header">
          <a :href="getMusicbrainzUrl('artist', data.id)" target="_blank" title="View on MusicBrainz">{{ data.name }}</a>
        </div>
        <div class="description">
          <table class="ui very basic fixed single line compact table">
            <tbody>
              <tr v-for="group in releasesGroups">
                <td>
                  {{ group['first-release-date'] }}
                </td>
                <td colspan="3">
                  <a :href="getMusicbrainzUrl('release-group', group.id)" class="discrete link" target="_blank" :title="$gettext('View on MusicBrainz')">
                    {{ group.title }}
                  </a>
                </td>
                  <td>
                  </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import CardMixin from './CardMixin'
import time from '@/utils/time'

export default Vue.extend({
  mixins: [CardMixin],
  data () {
    return {
      time
    }
  },
  computed: {
    type () {
      return 'artist'
    },
    releasesGroups () {
      return this.data['release-group-list'].filter(r => {
        return r.type === 'Album'
      })
    }
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.ui.card {
    width: 100% !important;
}
</style>
