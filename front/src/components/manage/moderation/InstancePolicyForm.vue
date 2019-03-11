<template>
  <form class="ui form" @submit.prevent="createOrUpdate">
    <h3 class="ui header">
      <translate v-if="object" key="1">Update moderation rule</translate>
      <translate v-else key="2">Add a new moderation rule</translate>
    </h3>
    <div v-if="errors && errors.length > 0" class="ui negative message">
      <div class="header"><translate>Error while creating rule</translate></div>
      <ul class="list">
        <li v-for="error in errors">{{ error }}</li>
      </ul>
    </div>

    <div class="field" v-if="object">
      <div class="ui toggle checkbox">
        <input id="policy-is-active" v-model="current.isActive" type="checkbox">
        <label for="policy-is-active">
          <translate v-if="current.isActive" key="1">Enabled</translate>
          <translate v-else key="2">Disabled</translate>
          <tooltip :content="labels.isActiveHelp" />
        </label>
      </div>
    </div>
    <div class="field">
      <label for="policy-summary">
        <translate>Reason</translate>
        <tooltip :content="labels.summaryHelp" />
      </label>
      <textarea name="policy-summary" id="policy-summary" rows="5" v-model="current.summary"></textarea>
    </div>
    <div class="field">
      <div class="ui toggle checkbox">
        <input id="policy-is-active" v-model="current.blockAll" type="checkbox">
        <label for="policy-is-active">
          <translate>Block everything</translate>
          <tooltip :content="labels.blockAllHelp" />
        </label>
      </div>
    </div>
    <div class="ui horizontal divider">
      <translate>Or customize your rule</translate>
    </div>
    <div v-for="config in fieldConfig" :class="['field']">
      <div class="ui toggle checkbox">
        <input :id="'policy-' + config.id" v-model="current[config.id]" type="checkbox">
        <label :for="'policy-' + config.id">
          <i :class="[config.icon, 'icon']"></i>
          {{ labels[config.id].label }}
          <tooltip :content="labels[config.id].help" />
        </label>
      </div>
    </div>
    <div class="ui hidden divider"></div>
    <button @click.prevent="$emit('cancel')" class="ui basic left floated button">
      <translate>Cancel</translate>
    </button>
    <button :class="['ui', 'right', 'floated', 'green', {'disabled loading': isLoading}, 'button']" :disabled="isLoading">
      <translate v-if="object" key="1">Update</translate>
      <translate v-else key="2">Create</translate>
    </button>
    <dangerous-button v-if="object" class="right floated basic button" color='red' @confirm="remove">
      <translate>Delete</translate>
      <p slot="modal-header">
        <translate>Delete this moderation rule?</translate>
      </p>
      <p slot="modal-content">
        <translate>This action is irreversible.</translate>
      </p>
      <p slot="modal-confirm">
        <translate>Delete moderation rule</translate>
      </p>
    </dangerous-button>
  </form>
</template>

<script>
import axios from 'axios'
import _ from 'lodash'

export default {
  props: {
    type: {type: String, required: true},
    object: {type: Object, default: null},
    target: {type: String, required: true},
  },
  data () {
    let current = this.object || {}
    return {
      isLoading: false,
      errors: [],
      current: {
        summary: _.get(current, 'summary', ''),
        isActive: _.get(current, 'is_active', true),
        blockAll: _.get(current, 'block_all', true),
        silenceActivity: _.get(current, 'silence_activity', false),
        silenceNotifications: _.get(current, 'silence_notifications', false),
        rejectMedia: _.get(current, 'reject_media', false),
      },
      fieldConfig: [
        // we hide those until we actually have the related features implemented :)
        // {id: "silenceActivity", icon: "feed"},
        // {id: "silenceNotifications", icon: "bell"},
        {id: "rejectMedia", icon: "file"},
      ]
    }
  },
  computed: {
    labels () {
      return {
        summaryHelp: this.$gettext("Explain why you're applying this policy. Depending on your instance configuration, this will help you remember why you acted on this account or domain, and may be displayed publicly to help users understand what moderation rules are in place."),
        isActiveHelp: this.$gettext("Use this setting to temporarily enable/disable the policy without completely removing it."),
        blockAllHelp: this.$gettext("Block everything from this account or domain. This will prevent any interaction with the entity, and purge related content (uploads, libraries, follows, etc.)"),
        silenceActivity: {
          help: this.$gettext("Hide account or domain content, except from followers."),
          label: this.$gettext("Mute activity"),
        },
        silenceNotifications: {
          help: this.$gettext("Prevent account or domain from triggering notifications, except from followers."),
          label: this.$gettext("Silence notifications"),
        },
        rejectMedia: {
          help: this.$gettext("Do not download any media file (audio, album cover, account avatar…) from this account or domain. This will purge existing content as well."),
          label: this.$gettext("Reject media"),
        }
      }
    }
  },
  methods: {
    createOrUpdate () {
      let self = this
      this.isLoading = true
      this.errors = []
      let url, method
      let data = {
        summary: this.current.summary,
        is_active: this.current.isActive,
        block_all: this.current.blockAll,
        silence_activity: this.current.silenceActivity,
        silence_notifications: this.current.silenceNotifications,
        reject_media: this.current.rejectMedia,
        target: {
          type: this.type,
          id: this.target,
        }
      }
      if (this.object) {
        url = `manage/moderation/instance-policies/${this.object.id}/`
        method = 'patch'
      } else {
        url = `manage/moderation/instance-policies/`
        method = 'post'
      }
      axios[method](url, data).then((response) => {
        this.isLoading = false
        self.$emit('save', response.data)
      }, (error) => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    },
    remove () {
      let self = this
      this.isLoading = true
      this.errors = []

      let url = `manage/moderation/instance-policies/${this.object.id}/`
      axios.delete(url).then((response) => {
        this.isLoading = false
        self.$emit('delete')
      }, (error) => {
        self.isLoading = false
        self.errors = error.backendErrors
      })
    }
  },
  watch: {
    'current.silenceActivity': function (v) {
      if (v) {
        this.current.blockAll = false
      }
    },
    'current.silenceNotifications': function (v) {
      if (v) {
        this.current.blockAll = false
      }
    },
    'current.rejectMedia': function (v) {
      if (v) {
        this.current.blockAll = false
      }
    },
    'current.blockAll': function (v) {
      if (v) {
        let self = this
        this.fieldConfig.forEach((f) => {
          self.current[f.id] = false
        })
      }
    }
  }
}
</script>

<style scoped>
.ui.placeholder.segment .field,
.ui.placeholder.segment textarea,
.ui.placeholder.segment > .ui.input,
.ui.placeholder.segment .button {
  max-width: 100%;
}
.segment .right.floated.button {
  margin-left: 1em;
}
</style>
