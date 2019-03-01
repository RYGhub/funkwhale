<template>
  <div class="ui card">
    <div class="content">
      <div v-if="isLoading" class="ui vertical segment">
        <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
      </div>
      <template v-if="data.id">
        <div class="header">
          <a :href="getMusicbrainzUrl('release', data.id)" target="_blank" :title="labels.musicbrainz">{{ data.title }}</a>
        </div>
        <div class="meta">
          <a :href="getMusicbrainzUrl('artist', data['artist-credit'][0]['artist']['id'])" target="_blank" :title="labels.musicbrainz">{{ data['artist-credit-phrase'] }}</a>
        </div>
        <div class="description">
          <table class="ui very basic fixed single line compact table">
            <tbody>
              <tr v-for="track in tracks">
                <td>
                  {{ track.position }}
                </td>
                <td colspan="3">
                  <a :href="getMusicbrainzUrl('recording', track.id)" class="discrete link" target="_blank" :title="labels.musicbrainz">
                    {{ track.recording.title }}
                  </a>
                </td>
                  <td>
                    {{ time.parse(parseInt(track.length) / 1000) }}
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
    labels () {
      return {
        musicbrainz: this.$pgettext('Content/*/Link.Tooltip/Verb', 'View on MusicBrainz')
      }
    },
    type () {
      return 'release'
    },
    tracks () {
      return this.data['medium-list'][0]['track-list']
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
