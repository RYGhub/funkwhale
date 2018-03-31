<template>
  <div>
    <div v-if="isLoading" class="ui vertical segment" v-title="'Radio'">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <div v-if="!isLoading && radio" class="ui head vertical center aligned stripe segment" v-title="radio.name">
      <div class="segment-content">
        <h2 class="ui center aligned icon header">
          <i class="circular inverted feed blue icon"></i>
          <div class="content">
            {{ radio.name }}
            <div class="sub header">
              Radio containing {{ tracks.length }} tracks,
              by <username :username="radio.user.username"></username>
            </div>
          </div>
        </h2>
        <div class="ui hidden divider"></div>
        <radio-button type="custom" :custom-radio-id="radio.id"></radio-button>
        <router-link class="ui icon button" :to="{name: 'library.radios.edit', params: {id: radio.id}}" exact>
          <i class="pencil icon"></i>
          Edit…
        </router-link>
        <dangerous-button class="labeled icon" :action="deleteRadio">
          <i class="trash icon"></i> Delete
          <p slot="modal-header">Do you want to delete the radio "{{ radio.name }}"?</p>
          <p slot="modal-content">This will completely delete this radio and cannot be undone.</p>
          <p slot="modal-confirm">Delete radio</p>
        </dangerous-button>
      </div>
    </div>
    <div class="ui vertical stripe segment">
      <h2>Tracks</h2>
      <track-table :tracks="tracks"></track-table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'

export default {
  props: {
    id: {required: true}
  },
  components: {
    TrackTable,
    RadioButton
  },
  data: function () {
    return {
      isLoading: false,
      radio: null,
      tracks: []
    }
  },
  created: function () {
    this.fetch()
  },
  methods: {
    fetch: function () {
      let self = this
      self.isLoading = true
      let url = 'radios/radios/' + this.id + '/'
      axios.get(url).then((response) => {
        self.radio = response.data
        axios.get(url + 'tracks').then((response) => {
          this.tracks = response.data.results
        }).then(() => {
          self.isLoading = false
        })
      })
    },
    deleteRadio () {
      let self = this
      let url = 'radios/radios/' + this.id + '/'
      axios.delete(url).then((response) => {
        self.$router.push({
          path: '/library'
        })
      })
    }
  }
}
</script>
