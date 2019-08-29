<template>
  <div class="ui fluid report card">
    <div class="content">
      <div class="header">
        <router-link :to="{name: 'manage.moderation.reports.detail', params: {id: obj.uuid}}">
          <translate translate-context="Content/Moderation/Card/Short" :translate-params="{id: obj.uuid.substring(0, 8)}">Report %{ id }</translate>
        </router-link>
      </div>
      <div class="content">
        <div class="ui stackable two column grid">
          <div class="column">
            <table class="ui very basic unstackable table">
              <tbody>
                <tr>
                  <td>
                    <translate translate-context="Content/Moderation/*">Submitted by</translate>
                  </td>
                  <td>
                    <div v-if="obj.submitter">
                      <actor-link :admin="true" :actor="obj.submitter" />
                    </div>
                    <div v-else="obj.submitter_email">
                      {{ obj.submitter_email }}
                    </div>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="*/*/*">Category</translate>
                  </td>
                  <td>
                    <i class="tag icon"></i>
                    {{ obj.type }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="*/*/*/Noun">Creation date</translate>
                  </td>
                  <td>
                    <human-date :date="obj.creation_date" :icon="true"></human-date>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="column">
            <table class="ui very basic unstackable table">
              <tbody>
                <tr>
                  <td>
                    <translate translate-context="*/*/*">Status</translate>
                  </td>
                  <td v-if="obj.is_handled">
                    <span v-if="obj.is_handled">
                      <i class="green check icon"></i>
                      <translate translate-context="Content/*/*/Short">Resolved</translate>
                    </span>
                  </td>
                  <td v-else>
                    <i class="red x icon"></i>
                    <translate translate-context="Content/*/*/Short">Unresolved</translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/Moderation/*">Assignee</translate>
                  </td>
                  <td>
                    <div v-if="obj.assigned_to">
                      <actor-link :admin="true" :actor="obj.assigned_to" />
                    </div>
                    <translate v-else translate-context="*/*/*">N/A</translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/*/*/Noun">Resolution date</translate>
                  </td>
                  <td>
                    <human-date v-if="obj.handled_date" :date="obj.handled_date" :icon="true"></human-date>
                    <translate v-else translate-context="*/*/*">N/A</translate>
                  </td>
                </tr>
                <tr>
                  <td>
                    <translate translate-context="Content/*/*/Noun">Internal notes</translate>
                  </td>
                  <td>
                    <i class="comment icon"></i>
                    {{ obj.notes.length }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div class="main content">
      <div class="ui stackable two column grid">
        <div class="column">
          <h3>
            <translate translate-context="Content/*/*/Short">Message</translate>
          </h3>
          <expandable-div v-if="obj.summary" class="summary" :content="obj.summary">
            <div v-html="markdown.makeHtml(obj.summary)"></div>
          </expandable-div>
        </div>
        <aside class="column">
          <h3>
            <translate translate-context="Content/*/*/Short">Reported object</translate>
          </h3>
          <div v-if="!obj.target" class="ui warning message">
            <translate translate-context="Content/Moderation/Message">The object associated with this report was deleted.</translate>
          </div>
          <router-link class="ui basic button" v-if="target && configs[target.type].urls.getAdminDetail" :to="configs[target.type].urls.getAdminDetail(obj.target_state)">
            <i class="wrench icon"></i>
            <translate translate-context="Content/Moderation/Link">Open in moderation interface</translate>
          </router-link>
          <table class="ui very basic unstackable table">
            <tbody>
              <tr v-if="target">
                <td>
                  <translate translate-context="*/*/*">Type</translate>
                </td>
                <td>
                  <i :class="[configs[target.type].icon, 'icon']"></i>
                  <translate translate-context="*/*/*">{{ configs[target.type].label }}</translate>
                </td>
              </tr>
              <tr v-if="target.type !== 'account'">
                <td>
                  <translate translate-context="*/*/*">Owner</translate>
                </td>
                <td>
                  <actor-link :admin="true" :actor="obj.target_owner"></actor-link>
                </td>
              </tr>
              <tr v-if="obj.target_state.is_local">
                <td>
                  <translate translate-context="Content/Moderation/*/Noun">Domain</translate>
                </td>
                <td>
                  <i class="home icon"></i>
                  <translate translate-context="Content/Moderation/*/Short, Noun">Local</translate>
                </td>
              </tr>
              <tr v-else-if="obj.target_state.domain">
                <td>
                  <router-link :to="{name: 'manage.moderation.domains.detail', params: {id: obj.target_state.domain }}">
                    <translate translate-context="Content/Moderation/*/Noun">Domain</translate>
                  </router-link>
                </td>
                <td>
                  {{ obj.target_state.domain }}
                </td>
              </tr>
              <tr v-for="field in targetFields" :key="field.id">
                <td>{{ field.label }}</td>
                <td>{{ field.repr }}</td>
              </tr>
            </tbody>
          </table>
          <h3>
            <translate translate-context="*/*/*">Actions</translate>

          </h3>
        </aside>
      </div>
      <div class="ui stackable two column grid">
        <div class="column">
          <h3>
            <translate translate-context="Content/*/*/Noun">Internal notes</translate>
          </h3>
          <notes-thread @deleted="handleRemovedNote($event)" :notes="obj.notes" />
          <note-form @created="obj.notes.push($event)" :target="{type: 'report', uuid: obj.uuid}" />
        </div>
      </div>
    </div>
    <div class="ui bottom attached buttons">
      <button
        v-if="obj.is_handled === false"
        @click="resolve(true)"
        :class="['ui', {loading: isLoading}, 'green', 'basic', 'button']">
        <translate translate-context="Content/*/Button.Label/Verb">Resolve</translate>
      </button>
      <button
        v-if="obj.is_handled === true"
        @click="resolve(false)"
        :class="['ui', {loading: isLoading}, 'yellow', 'basic', 'button']">
        <translate translate-context="Content/*/Button.Label">Unresolve</translate>
      </button>
      <dangerous-button
        :class="['ui', {loading: isLoading}, 'basic button']"
        :action="remove">
        <translate translate-context="*/*/*/Verb">Delete</translate>
        <p slot="modal-header"><translate translate-context="Popup/*/Title">Delete this report?</translate></p>
        <div slot="modal-content">
          <p><translate translate-context="Popup/*/Paragraph">The report will be completely removed, this action is irreversible.</translate></p>
        </div>
        <p slot="modal-confirm"><translate translate-context="*/*/*/Verb">Delete</translate></p>
      </dangerous-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { diffWordsWithSpace } from 'diff'
import NoteForm from '@/components/manage/moderation/NoteForm'
import NotesThread from '@/components/manage/moderation/NotesThread'
import entities from '@/entities'
import showdown from 'showdown'

function castValue (value) {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value)
}

export default {
  props: {
    obj: {required: true},
    currentState: {required: false}
  },
  components: {
    NoteForm,
    NotesThread,
  },
  data () {
      return {
      markdown: new showdown.Converter(),
      isLoading: false,
    }
  },
  computed: {
    configs: entities.getConfigs,
    previousState () {
      if (this.obj.is_applied) {
        // mutation was applied, we use the previous state that is stored
        // on the mutation itself
        return this.obj.previous_state
      }
      // mutation is not applied yet, so we use the current state that was
      // passed to the component, if any
      return this.currentState
    },
    detailUrl () {
      if (!this.target) {
        return ''
      }
      let namespace
      let id = this.target.id
      if (this.target.type === 'track') {
        namespace = 'library.tracks.edit.detail'
      }
      if (this.target.type === 'album') {
        namespace = 'library.albums.edit.detail'
      }
      if (this.target.type === 'artist') {
        namespace = 'library.artists.edit.detail'
      }
      return this.$router.resolve({name: namespace, params: {id, editId: this.obj.uuid}}).href
    },

    targetFields () {
      if (!this.target) {
        return []
      }
      let payload = this.obj.target_state
      let fields = this.configs[this.target.type].moderatedFields
      let self = this
      return fields.map((fieldConfig) => {
        let dummyRepr = (v) => { return v }
        let getValueRepr = fieldConfig.getValueRepr || dummyRepr
        let d = {
          id: fieldConfig.id,
          label: fieldConfig.label,
          value: payload[fieldConfig.id],
          repr: castValue(getValueRepr(payload[fieldConfig.id])),
        }
        return d
      })
    },
    target () {
      if (this.obj.target) {
        return this.obj.target
      } else {
        return this.obj.target_state._target
      }
    }
  },
  methods: {
    remove () {
      let self = this
      this.isLoading = true
      axios.delete(`manage/moderation/reports/${this.obj.uuid}/`).then((response) => {
        self.$emit('deleted')
        self.isLoading = false
        if (!self.obj.is_handled) {
          self.$store.commit('ui/incrementNotifications', {count: -1, type: 'pendingReviewReports'})
        }
      }, error => {
        self.isLoading = false
      })
    },
    resolve (v) {
      let url = `manage/moderation/reports/${this.obj.uuid}/`
      let self = this
      this.isLoading = true
      axios.patch(url, {is_handled: v}).then((response) => {
        self.$emit('handled', v)
        self.isLoading = false
        let increment
        if (v) {
          increment = -1
        } else {
          increment = 1
        }
        self.$store.commit('ui/incrementNotifications', {count: increment, type: 'pendingReviewReports'})
      }, error => {
        self.isLoading = false
      })
    },
    handleRemovedNote (uuid) {
      this.obj.notes = this.obj.notes.filter((note) => {
        return note.uuid != uuid
      })
    }
  }
}
</script>
