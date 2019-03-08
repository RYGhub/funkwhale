<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">
      <section :class="['ui', 'head', 'vertical', 'stripe', 'segment']" v-title="object.full_username">
        <div class="ui stackable two column grid">
          <div class="ui column">
            <div class="segment-content">
              <h2 class="ui header">
                <i class="circular inverted user icon"></i>
                <div class="content">
                  {{ object.full_username }}
                  <div class="sub header">
                    <template v-if="object.user">
                      <span class="ui tiny teal icon label">
                        <i class="home icon"></i>
                        <translate translate-context="Content/Moderation/List item">Local account</translate>
                      </span>
                      &nbsp;
                    </template>
                    <a :href="object.url || object.fid" target="_blank" rel="noopener noreferrer">
                      <translate translate-context="Content/Moderation/Link/Verb">Open profile</translate>&nbsp;
                      <i class="external icon"></i>
                    </a>
                  </div>
                </div>
              </h2>
            </div>
          </div>
          <div class="ui column">
            <div v-if="!object.user" class="ui compact clearing placeholder segment">
              <template v-if="isLoadingPolicy">
                <div class="paragraph">
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
              </template>
              <template v-else-if="!policy && !showPolicyForm">
                <header class="ui header">
                  <h3>
                    <i class="shield icon"></i>
                    <translate translate-context="Content/Moderation/Card.Title">You don't have any rule in place for this account.</translate>
                  </h3>
                </header>
                <p><translate translate-context="Content/Moderation/Card.Paragraph">Moderation policies help you control how your instance interact with a given domain or account.</translate></p>
                <button @click="showPolicyForm = true" class="ui primary button"><translate translate-context="Content/Moderation/Button/Verb">Add a moderation policy</translate></button>
              </template>
              <instance-policy-card v-else-if="policy && !showPolicyForm" :object="policy" @update="showPolicyForm = true">
                <header class="ui header">
                  <h3>
                    <translate translate-context="Content/Moderation/Card.Title">This domain is subject to specific moderation rules</translate>
                  </h3>
                </header>
              </instance-policy-card>
              <instance-policy-form
                v-else-if="showPolicyForm"
                @cancel="showPolicyForm = false"
                @save="updatePolicy"
                @delete="policy = null; showPolicyForm = false"
                :object="policy"
                type="actor"
                :target="object.full_username" />
            </div>
          </div>
        </div>
      </section>
      <div class="ui vertical stripe segment">
        <div class="ui stackable three column grid">
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="info icon"></i>
                <div class="content">
                  <translate translate-context="Content/Moderation/Title">Account data</translate>
                </div>
              </h3>
              <table class="ui very basic table">
                <tbody>
                  <tr>
                    <td>
                      <translate translate-context="Content/*/*">Username</translate>
                    </td>
                    <td>
                      {{ object.preferred_username }}
                    </td>
                  </tr>
                  <tr v-if="!object.user">
                    <td>
                      <translate translate-context="Content/*/*">Domain</translate>
                    </td>
                    <td>
                      <router-link :to="{name: 'manage.moderation.domains.detail', params: {id: object.domain }}">
                        {{ object.domain }}
                      </router-link>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="'Content/*/*/Noun'">Display name</translate>
                    </td>
                    <td>
                      {{ object.name }}
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/*/*">Email address</translate>
                    </td>
                    <td>
                      {{ object.user.email }}
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/*/*/Noun">Login status</translate>
                    </td>
                    <td>
                      <div class="ui toggle checkbox" v-if="object.user.username != $store.state.auth.profile.username">
                        <input
                          @change="updateUser('is_active')"
                          v-model="object.user.is_active" type="checkbox">
                        <label>
                          <translate v-if="object.user.is_active" key="1" translate-context="Content/*/Label">Enabled</translate>
                          <translate v-else key="2" translate-context="Content/*/Label">Disabled</translate>
                        </label>
                      </div>
                      <translate v-else-if="object.user.is_active" key="1" translate-context="Content/*/Label">Enabled</translate>
                      <translate v-else key="2" translate-context="Content/*/Label">Disabled</translate>
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label">Permissions</translate>
                    </td>
                    <td>
                      <select
                        @change="updateUser('permissions')"
                        v-model="permissions"
                        multiple
                        class="ui search selection dropdown">
                        <option v-for="p in allPermissions" :value="p.code">{{ p.label }}</option>
                      </select>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Type</translate>
                    </td>
                    <td>
                      {{ object.type }}
                    </td>
                  </tr>
                  <tr v-if="!object.user">
                    <td>
                      <translate translate-context="Content/*/Table.Label">First seen</translate>
                    </td>
                    <td>
                      <human-date :date="object.creation_date"></human-date>
                    </td>
                  </tr>
                  <tr v-if="!object.user">
                    <td>
                      <translate translate-context="Content/*/Table.Label">Last checked</translate>
                    </td>
                    <td>
                      <human-date v-if="object.last_fetch_date" :date="object.last_fetch_date"></human-date>
                      <translate v-else translate-context="*/*/*">N/A</translate>
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/*/Table.Label">Sign-up date</translate>
                    </td>
                    <td>
                      <human-date :date="object.user.date_joined"></human-date>
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/*/Table.Label">Last activity</translate>
                    </td>
                    <td>
                      <human-date :date="object.user.last_activity"></human-date>
                    </td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="feed icon"></i>
                <div class="content">
                  <translate translate-context="Content/Moderation/Title">Activity</translate>&nbsp;
                  <span :data-tooltip="labels.statsWarning"><i class="question circle icon"></i></span>

                </div>
              </h3>
              <div v-if="isLoadingStats" class="ui placeholder">
                <div class="full line"></div>
                <div class="short line"></div>
                <div class="medium line"></div>
                <div class="long line"></div>
              </div>
              <table v-else class="ui very basic table">
                <tbody>
                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Emitted messages</translate>
                    </td>
                    <td>
                      {{ stats.outbox_activities}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Received library follows</translate>
                    </td>
                    <td>
                      {{ stats.received_library_follows}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Emitted library follows</translate>
                    </td>
                    <td>
                      {{ stats.emitted_library_follows}}
                    </td>
                  </tr>
                </tbody>
              </table>
            </section>
          </div>
          <div class="column">
            <section>
              <h3 class="ui header">
                <i class="music icon"></i>
                <div class="content">
                  <translate translate-context="Content/Moderation/Title">Audio content</translate>&nbsp;
                  <span :data-tooltip="labels.statsWarning"><i class="question circle icon"></i></span>

                </div>
              </h3>
              <div v-if="isLoadingStats" class="ui placeholder">
                <div class="full line"></div>
                <div class="short line"></div>
                <div class="medium line"></div>
                <div class="long line"></div>
              </div>
              <table v-else class="ui very basic table">
                <tbody>

                  <tr v-if="!object.user">
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Cached size</translate>
                    </td>
                    <td>
                      {{ stats.media_downloaded_size | humanSize }}
                    </td>
                  </tr>
                  <tr v-if="object.user">
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun" >Upload quota</translate>
                      <span :data-tooltip="labels.uploadQuota"><i class="question circle icon"></i></span>
                    </td>
                    <td>
                      <div class="ui right labeled input">
                        <input
                          class="ui input"
                          @change="updateUser('upload_quota', true)"
                          v-model.number="object.user.upload_quota"
                          step="100"
                          type="number" />
                        <div class="ui basic label">
                          <translate translate-context="Content/*/*/Unit">MB</translate>
                        </div>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/*/*">Total size</translate>
                    </td>
                    <td>
                      {{ stats.media_total_size | humanSize }}
                    </td>
                  </tr>

                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label">Libraries</translate>
                    </td>
                    <td>
                      {{ stats.libraries }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/Moderation/Table.Label/Noun">Uploads</translate>
                    </td>
                    <td>
                      {{ stats.uploads }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/*/*">Artists</translate>
                    </td>
                    <td>
                      {{ stats.artists }}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/*/*">Albums</translate>
                    </td>
                    <td>
                      {{ stats.albums}}
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <translate translate-context="Content/*/*">Tracks</translate>
                    </td>
                    <td>
                      {{ stats.tracks }}
                    </td>
                  </tr>
                </tbody>
              </table>

            </section>
          </div>
        </div>
      </div>

    </template>
  </main>
</template>

<script>
import axios from "axios"
import logger from "@/logging"
import lodash from '@/lodash'
import $ from "jquery"

import InstancePolicyForm from "@/components/manage/moderation/InstancePolicyForm"
import InstancePolicyCard from "@/components/manage/moderation/InstancePolicyCard"

export default {
  props: ["id"],
  components: {
    InstancePolicyForm,
    InstancePolicyCard,
  },
  data() {
    return {
      lodash,
      isLoading: true,
      isLoadingStats: false,
      isLoadingPolicy: false,
      object: null,
      stats: null,
      showPolicyForm: false,
      permissions: [],
    }
  },
  created() {
    this.fetchData()
    this.fetchStats()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      let url = "manage/accounts/" + this.id + "/"
      axios.get(url).then(response => {
        self.object = response.data
        self.isLoading = false
        if (self.object.instance_policy) {
          self.fetchPolicy(self.object.instance_policy)
        }
        if (response.data.user) {
          self.allPermissions.forEach(p => {
            if (self.object.user.permissions[p.code]) {
              self.permissions.push(p.code)
            }
          })
        }
      })
    },
    fetchPolicy(id) {
      var self = this
      this.isLoadingPolicy = true
      let url = `manage/moderation/instance-policies/${id}/`
      axios.get(url).then(response => {
        self.policy = response.data
        self.isLoadingPolicy = false
      })
    },
    fetchStats() {
      var self = this
      this.isLoadingStats = true
      let url = "manage/accounts/" + this.id + "/stats/"
      axios.get(url).then(response => {
        self.stats = response.data
        self.isLoadingStats = false
      })
    },
    refreshNodeInfo (data) {
      this.object.nodeinfo = data
      this.object.nodeinfo_fetch_date = new Date()
    },

    updateUser(attr, toNull) {
      let newValue = this.object.user[attr]
      if (toNull && !newValue) {
        newValue = null
      }
      let params = {}
      if (attr === "permissions") {
        params["permissions"] = {}
        this.allPermissions.forEach(p => {
          params["permissions"][p.code] = this.permissions.indexOf(p.code) > -1
        })
      } else {
        params[attr] = newValue
      }
      axios.patch(`manage/users/users/${this.object.user.id}/`, params).then(
        response => {
          logger.default.info(
            `${attr} was updated succcessfully to ${newValue}`
          )
        },
        error => {
          logger.default.error(
            `Error while setting ${attr} to ${newValue}`,
            error
          )
        }
      )
    }
  },
  computed: {
    labels() {
      return {
        statsWarning: this.$pgettext('Content/Moderation/Help text', 'Statistics are computed from known activity and content on your instance, and do not reflect general activity for this account'),
        uploadQuota: this.$pgettext('Content/Moderation/Help text', 'Determine how much content the user can upload. Leave empty to use the default value of the instance.'),
      }
    },
    allPermissions() {
      return [
        {
          code: "library",
          label: this.$pgettext('Content/Moderation/Dropdown', "Library")
        },
        {
          code: "moderation",
          label: this.$pgettext('Content/Moderation/Dropdown', "Moderation")
        },
        {
          code: "settings",
          label: this.$pgettext('Content/Moderation/Dropdown', "Settings")
        }
      ]
    }
  },
  watch: {
    object () {
      this.$nextTick(() => {
        $(this.$el).find("select.dropdown").dropdown()
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.placeholder.segment {
  width: 100%;
}
</style>
