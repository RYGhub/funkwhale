<template>
  <table class="ui compact very basic single line unstackable table">
    <thead>
      <tr v-if="actions.length > 0">
        <th colspan="1000">
          <div class="ui small form">
            <div class="ui inline fields">
              <div class="field">
                <label>{{ $t('Actions') }}</label>
                <select class="ui dropdown" v-model="currentActionName">
                  <option v-for="action in actions" :value="action.name">
                    {{ action.label }}
                  </option>
                </select>
              </div>
              <div class="field">
                <div
                  v-if="!selectAll"
                  @click="launchAction"
                  :disabled="checked.length === 0"
                  :class="['ui', {disabled: checked.length === 0}, {'loading': actionLoading}, 'button']">
                  {{ $t('Go') }}</div>
                <dangerous-button
                  v-else-if="!currentAction.isDangerous" :class="['ui', {disabled: checked.length === 0}, {'loading': actionLoading}, 'button']"
                  confirm-color="green"
                  color=""
                  @confirm="launchAction">
                  {{ $t('Go') }}
                  <p slot="modal-header">{{ $t('Do you want to launch action "{% action %}" on {% total %} elements?', {action: currentActionName, total: objectsData.count}) }}
                  <p slot="modal-content">
                    {{ $t('This may affect a lot of elements, please double check this is really what you want.')}}
                  </p>
                  <p slot="modal-confirm">{{ $t('Launch') }}</p>
                </dangerous-button>
              </div>
              <div class="count field">
                <span v-if="selectAll">{{ $t('{% count %} on {% total %} selected', {count: objectsData.count, total: objectsData.count}) }}</span>
                <span v-else>{{ $t('{% count %} on {% total %} selected', {count: checked.length, total: objectsData.count}) }}</span>
                <template v-if="!currentAction.isDangerous && checkable.length === checked.length">
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
              :disabled="checkable.length === 0"
              :checked="checkable.length > 0 && checked.length === checkable.length"><label>&nbsp;</label>
          </div>
        </th>
        <slot name="header-cells"></slot>
      </tr>
    </thead>
    <tbody v-if="objectsData.count > 0">
      <tr v-for="(obj, index) in objectsData.results">
        <td class="collapsing">
          <input
            type="checkbox"
            :disabled="checkable.indexOf(obj.id) === -1"
            @click="toggleCheck($event, obj.id, index)"
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
      currentActionName: null,
      selectAll: false,
      lastCheckedIndex: -1
    }
    if (this.actions.length > 0) {
      d.currentActionName = this.actions[0].name
    }
    return d
  },
  methods: {
    toggleCheckAll () {
      this.lastCheckedIndex = -1
      if (this.checked.length === this.checkable.length) {
        // we uncheck
        this.checked = []
      } else {
        this.checked = this.checkable.map(i => { return i })
      }
    },
    toggleCheck (event, id, index) {
      let self = this
      let affectedIds = [id]
      let newValue = null
      if (this.checked.indexOf(id) > -1) {
        // we uncheck
        this.selectAll = false
        newValue = false
      } else {
        newValue = true
      }
      if (event.shiftKey && this.lastCheckedIndex > -1) {
        // we also add inbetween ids to the list of affected ids
        let idxs = [index, this.lastCheckedIndex]
        idxs.sort((a, b) => a - b)
        let objs = this.objectsData.results.slice(idxs[0], idxs[1] + 1)
        affectedIds = affectedIds.concat(objs.map((o) => { return o.id }))
      }
      affectedIds.forEach((i) => {
        let checked = self.checked.indexOf(i) > -1
        if (newValue && !checked && self.checkable.indexOf(i) > -1) {
          return self.checked.push(i)
        }
        if (!newValue && checked) {
          self.checked.splice(self.checked.indexOf(i), 1)
        }
      })
      this.lastCheckedIndex = index
    },
    launchAction () {
      let self = this
      self.actionLoading = true
      self.result = null
      let payload = {
        action: this.currentActionName,
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
        self.$emit('action-launched', response.data)
      }, error => {
        self.actionLoading = false
        self.actionErrors = error.backendErrors
      })
    }
  },
  computed: {
    currentAction () {
      let self = this
      return this.actions.filter((a) => {
        return a.name === self.currentActionName
      })[0]
    },
    checkable () {
      let objs = this.objectsData.results
      let filter = this.currentAction.filterCheckable
      if (filter) {
        objs = objs.filter((o) => {
          return filter(o)
        })
      }
      return objs.map((o) => { return o.id })
    }
  },
  watch: {
    objectsData: {
      handler () {
        this.checked = []
        this.selectAll = false
      },
      deep: true
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
