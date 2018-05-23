<template>
  <table class="ui compact very basic single line unstackable table">
    <thead>
      <tr v-if="actions.length > 0 && objectsData.count > 0">
        <th colspan="1000">
          <div class="ui small form">
            <div class="ui inline fields">
              <div class="field">
                <label>{{ $t('Actions') }}</label>
                <select class="ui dropdown" v-model="currentAction">
                  <option v-for="action in actions" :value="action[0]">
                    {{ action[1] }}
                  </option>
                </select>
              </div>
              <div class="field">
                <div
                  @click="launchAction"
                  :disabled="checked.length === 0"
                  :class="['ui', {disabled: checked.length === 0}, {'loading': actionLoading}, 'button']">
                  {{ $t('Go') }}</div>
              </div>
              <div class="count field">
                <span v-if="selectAll">{{ $t('{% count %} on {% total %} selected', {count: objectsData.count, total: objectsData.count}) }}</span>
                <span v-else>{{ $t('{% count %} on {% total %} selected', {count: checked.length, total: objectsData.count}) }}</span>
                <template v-if="checked.length === objectsData.results.length">
                  <a @click="selectAll = true" v-if="!selectAll">
                    {{ $t('Select all {% total %} elements', {total: objectsData.count}) }}
                  </a>
                  <a @click="selectAll = false" v-else>
                    {{ $t('Select only current page') }}
                  </a>
                </template>
              </div>
            </div>
            <div v-if="actionErrors.length > 0" class="ui negative message">
              <div class="header">{{ $t('Error while applying action') }}</div>
              <ul class="list">
                <li v-for="error in actionErrors">{{ error }}</li>
              </ul>
            </div>
            <div v-if="actionResult" class="ui positive message">
              <p>{{ $t('Action {% action %} was launched successfully on {% count %} objects.', {action: actionResult.action, count: actionResult.updated}) }}</p>
              <slot name="action-success-footer" :result="actionResult">
              </slot>
            </div>
          </div>
        </th>
      </tr>
      <tr>
        <th>
          <div class="ui checkbox">
            <input
              type="checkbox"
              @change="toggleCheckAll"
              :checked="objectsData.results.length === checked.length"><label>&nbsp;</label>
          </div>
        </th>
        <slot name="header-cells"></slot>
      </tr>
    </thead>
    <tbody>
      <tr v-for="obj in objectsData.results">
        <td class="collapsing">
          <input
            type="checkbox"
            @change="toggleCheck(obj.id)"
            :checked="checked.indexOf(obj.id) > -1"><label>&nbsp;</label>
          </div>
        </td>
        <slot name="row-cells" :obj="obj"></slot>
      </tr>
    </tbody>
  </table>
</template>
<script>
import axios from 'axios'

export default {
  props: {
    actionUrl: {type: String, required: true},
    objectsData: {type: Object, required: true},
    actions: {type: Array, required: true, default: () => { return [] }},
    filters: {type: Object, required: false, default: () => { return {} }}
  },
  components: {},
  data () {
    let d = {
      checked: [],
      actionLoading: false,
      actionResult: null,
      actionErrors: [],
      currentAction: null,
      selectAll: false
    }
    if (this.actions.length > 0) {
      d.currentAction = this.actions[0][0]
    }
    return d
  },
  methods: {
    toggleCheckAll () {
      if (this.checked.length === this.objectsData.results.length) {
        // we uncheck
        this.checked = []
      } else {
        this.checked = this.objectsData.results.map(t => { return t.id })
      }
    },
    toggleCheck (id) {
      if (this.checked.indexOf(id) > -1) {
        // we uncheck
        this.selectAll = false
        this.checked.splice(this.checked.indexOf(id), 1)
      } else {
        this.checked.push(id)
      }
    },
    launchAction () {
      let self = this
      self.actionLoading = true
      self.result = null
      let payload = {
        action: this.currentAction,
        filters: this.filters
      }
      if (this.selectAll) {
        payload.objects = 'all'
      } else {
        payload.objects = this.checked
      }
      axios.post(this.actionUrl, payload).then((response) => {
        self.actionResult = response.data
        self.actionLoading = false
      }, error => {
        self.actionLoading = false
        self.actionErrors = error.backendErrors
      })
    }
  }
}
</script>
<style scoped>
.count.field {
  font-weight: normal;
}
.ui.form .inline.fields {
  margin: 0;
}
</style>
