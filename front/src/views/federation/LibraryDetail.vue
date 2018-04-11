<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="'Library'">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">
      <div :class="['ui', 'head', 'vertical', 'center', 'aligned', 'stripe', 'segment']" v-title="libraryUsername">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted cloud olive icon"></i>
            <div class="content">
              {{ libraryUsername }}
            </div>
          </h2>
        </div>
        <div class="ui hidden divider"></div>
        <div class="ui one column centered grid">
          <table class="ui collapsing very basic table">
            <tbody>
              <tr>
                <td>Follow status</td>
                <td>
                  <template v-if="object.follow.approved === null">
                    <i class="loading icon"></i> Pending approval
                  </template>
                  <template v-else-if="object.follow.approved === true">
                    <i class="check icon"></i> Following
                  </template>
                  <template v-else-if="object.follow.approved === false">
                    <i class="x icon"></i> Not following
                  </template>
                </td>
                <td>
                </td>
              </tr>
              <tr>
                <td>Federation</td>
                <td>
                  <div class="ui toggle checkbox">
                    <input
                      @change="update('federation_enabled')"
                      v-model="object.federation_enabled" type="checkbox">
                    <label></label>
                  </div>
                </td>
                <td>
                </td>
              </tr>
              <tr>
                <td>Auto importing</td>
                <td>
                  <div class="ui toggle checkbox">
                    <input
                      @change="update('autoimport')"
                      v-model="object.autoimport" type="checkbox">
                    <label></label>
                  </div>
                </td>
                <td></td>
              </tr>
              <tr>
                <td>File mirroring</td>
                <td>
                  <div class="ui toggle checkbox">
                    <input
                      @change="update('download_files')"
                      v-model="object.download_files" type="checkbox">
                    <label></label>
                  </div>
                </td>
                <td></td>
              </tr>
              <tr>
                <td>Library size</td>
                <td>
                  {{ object.tracks_count }} tracks
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="ui vertical stripe segment">
        <h2>Tracks available in this library</h2>
        <div class="ui stackable doubling three column grid">
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import axios from 'axios'
import logger from '@/logging'

export default {
  props: ['id'],
  components: {},
  data () {
    return {
      isLoading: true,
      object: null
    }
  },
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      let url = 'federation/libraries/' + this.id + '/'
      logger.default.debug('Fetching library "' + this.id + '"')
      axios.get(url).then((response) => {
        self.object = response.data
        self.isLoading = false
      })
    },
    update (attr) {
      let newValue = this.object[attr]
      let params = {}
      let self = this
      params[attr] = newValue
      axios.patch('federation/libraries/' + this.id + '/', params).then((response) => {
        console.log(`${attr} was updated succcessfully to ${newValue}`)
      }, (error) => {
        console.log(`Error while setting ${attr} to ${newValue}`, error)
        self.object[attr] = !newValue
      })
    }
  },
  computed: {
    libraryUsername () {
      let actor = this.object.actor
      return `${actor.preferred_username}@${actor.domain}`
    }
  },
  watch: {
    id () {
      this.fetchData()
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
