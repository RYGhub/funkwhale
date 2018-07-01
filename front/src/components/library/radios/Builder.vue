<template>
  <div class="ui vertical stripe segment" v-title="labels.title">
    <div>
      <div>
        <h2 class="ui header">
          <translate>Builder</translate>
        </h2>
        <p><translate>You can use this interface to build your own custom radio, which will play tracks according to your criteria.</translate></p>
          <div class="ui form">
          <div class="inline fields">
            <div class="field">
              <label for="name"><translate>Radio name</translate></label>
              <input id="name" type="text" v-model="radioName" :placeholder="labels.placeholder" />
            </div>
            <div class="field">
              <input id="public" type="checkbox" v-model="isPublic" />
              <label for="public"><translate>Display publicly</translate></label>
            </div>
            <button :disabled="!canSave" @click="save" class="ui green button">
              <translate>Save</translate>
            </button>
            <radio-button v-if="id" type="custom" :custom-radio-id="id"></radio-button>
          </div>
        </div>
        <div class="ui form">
          <p>
            <translate>Add filters to customize your radio</translate>
          </p>
          <div class="inline field">
            <select class="ui dropdown" v-model="currentFilterType">
              <option value="">
                <translate>Select a filter</translate>
              </option>
              <option v-for="f in availableFilters" :value="f.type">{{ f.label }}</option>
            </select>
            <button :disabled="!currentFilterType" @click="add" class="ui button">
              <translate>Add filter</translate>
            </button>
          </div>
          <p v-if="currentFilter">
            {{ currentFilter.help_text }}
          </p>
        </div>
        <table class="ui table">
          <thead>
            <tr>
              <th class="two wide"><translate>Filter name</translate></th>
              <th class="one wide"><translate>Exclude</translate></th>
              <th class="six wide"><translate>Config</translate></th>
              <th class="five wide"><translate>Candidates</translate></th>
              <th class="two wide"><translate>Actions</translate></th>
            </tr>
          </thead>
          <tbody>
            <builder-filter
              v-for="(f, index) in filters"
              :key="(f, index, f.hash)"
              :index="index"
              @update-config="updateConfig"
              @delete="deleteFilter"
              :config="f.config"
              :filter="f.filter">
            </builder-filter>
          </tbody>
        </table>
        <template v-if="checkResult">
          <h3
            class="ui header"
            v-translate="{count: checkResult.candidates.count}"
            :translate-n="checkResult.candidates.count"
            translate-plural="%{ count } tracks matching combined filters">
            %{ count } track matching combined filters
          </h3>
          <track-table v-if="checkResult.candidates.sample" :tracks="checkResult.candidates.sample"></track-table>
        </template>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
import $ from 'jquery'
import _ from 'lodash'
import BuilderFilter from './Filter'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'

export default {
  props: {
    id: {required: false}
  },
  components: {
    BuilderFilter,
    TrackTable,
    RadioButton
  },
  data: function () {
    return {
      availableFilters: [],
      currentFilterType: null,
      filters: [],
      checkResult: null,
      radioName: '',
      isPublic: true
    }
  },
  created: function () {
    let self = this
    this.fetchFilters().then(() => {
      if (self.id) {
        self.fetch()
      }
    })
  },
  mounted () {
    $('.ui.dropdown').dropdown()
  },
  methods: {
    fetchFilters: function () {
      let self = this
      let url = 'radios/radios/filters/'
      return axios.get(url).then((response) => {
        self.availableFilters = response.data
      })
    },
    add () {
      this.filters.push({
        config: {},
        filter: this.currentFilter,
        hash: +new Date()
      })
      this.fetchCandidates()
    },
    updateConfig (index, field, value) {
      this.filters[index].config[field] = value
      this.fetchCandidates()
    },
    deleteFilter (index) {
      this.filters.splice(index, 1)
      this.fetchCandidates()
    },
    fetch: function () {
      let self = this
      let url = 'radios/radios/' + this.id + '/'
      axios.get(url).then((response) => {
        self.filters = response.data.config.map(f => {
          return {
            config: f,
            filter: this.availableFilters.filter(e => { return e.type === f.type })[0],
            hash: +new Date()
          }
        })
        self.radioName = response.data.name
        self.isPublic = response.data.is_public
      })
    },
    fetchCandidates: function () {
      let self = this
      let url = 'radios/radios/validate/'
      let final = this.filters.map(f => {
        let c = _.clone(f.config)
        c.type = f.filter.type
        return c
      })
      final = {
        'filters': [
          {'type': 'group', filters: final}
        ]
      }
      axios.post(url, final).then((response) => {
        self.checkResult = response.data.filters[0]
      })
    },
    save: function () {
      let self = this
      let final = this.filters.map(f => {
        let c = _.clone(f.config)
        c.type = f.filter.type
        return c
      })
      final = {
        'name': this.radioName,
        'is_public': this.isPublic,
        'config': final
      }
      if (this.id) {
        let url = 'radios/radios/' + this.id + '/'
        axios.put(url, final).then((response) => {
        })
      } else {
        let url = 'radios/radios/'
        axios.post(url, final).then((response) => {
          self.$router.push({
            name: 'library.radios.detail',
            params: {
              id: response.data.id
            }
          })
        })
      }
    }
  },
  computed: {
    labels () {
      let title = this.$gettext('Radio Builder')
      let placeholder = this.$gettext('My awesome radio')
      return {
        title,
        placeholder
      }
    },
    canSave: function () {
      return (
        this.radioName.length > 0 && this.checkErrors.length === 0
      )
    },
    checkErrors: function () {
      if (!this.checkResult) {
        return []
      }
      let errors = this.checkResult.errors
      return errors
    },
    currentFilter: function () {
      let self = this
      return this.availableFilters.filter(e => {
        return e.type === self.currentFilterType
      })[0]
    }
  },
  watch: {
    filters: {
      handler: function () {
        this.fetchCandidates()
      },
      deep: true
    }
  }
}
</script>
