<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">
      <section :class="['ui', 'head', 'vertical', 'center', 'aligned', 'stripe', 'segment']" v-title="object.username">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted user red icon"></i>
            <div class="content">
              @{{ object.username }}
            </div>
          </h2>
        </div>
        <div class="ui hidden divider"></div>
        <div class="ui one column centered grid">
          <table class="ui collapsing very basic table">
            <tbody>
              <tr>
                <td>
                  <translate>Name</translate>
                </td>
                <td>
                  {{ object.name }}
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Email address</translate>
                </td>
                <td>
                  {{ object.email }}
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Sign-up</translate>
                </td>
                <td>
                  <human-date :date="object.date_joined"></human-date>
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Last activity</translate>
                </td>
                <td>
                  <human-date v-if="object.last_activity" :date="object.last_activity"></human-date>
                  <template v-else><translate>N/A</translate></template>
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Account active</translate>
                  <span :data-tooltip="labels.inactive"><i class="question circle icon"></i></span>
                </td>
                <td>
                  <div class="ui toggle checkbox">
                    <input
                      @change="update('is_active')"
                      v-model="object.is_active" type="checkbox">
                    <label></label>
                  </div>
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Permissions</translate>
                </td>
                <td>
                  <select
                    @change="update('permissions')"
                    v-model="permissions"
                    multiple
                    class="ui search selection dropdown">
                    <option v-for="p in allPermissions" :value="p.code">{{ p.label }}</option>
                  </select>
                </td>
              </tr>
              <tr>
                <td>
                  <translate>Upload quota</translate>
                  <span :data-tooltip="labels.uploadQuota"><i class="question circle icon"></i></span>
                </td>
                <td>
                  <div class="ui right labeled input">
                  <input
                    class="ui input"
                    @change="update('upload_quota', true)"
                    v-model.number="object.upload_quota"
                    step="100"
                    type="number" />
                  <div class="ui basic label">
                    <translate>MB</translate>
                  </div>
                </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="ui hidden divider"></div>
        <button @click="fetchData" class="ui basic button"><translate>Refresh</translate></button>
      </section>
    </template>
  </main>
</template>

<script>
import $ from "jquery"
import axios from "axios"
import logger from "@/logging"

export default {
  props: ["id"],
  data() {
    return {
      isLoading: true,
      object: null,
      permissions: []
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      let url = "manage/users/users/" + this.id + "/"
      axios.get(url).then(response => {
        self.object = response.data
        self.permissions = []
        self.allPermissions.forEach(p => {
          if (self.object.permissions[p.code]) {
            self.permissions.push(p.code)
          }
        })
        self.isLoading = false
      })
    },
    update(attr, toNull) {
      let newValue = this.object[attr]
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
      axios.patch("manage/users/users/" + this.id + "/", params).then(
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
        inactive: this.$gettext(
          "Determine if the user account is active or not. Inactive users cannot login or use the service."
        ),
        uploadQuota: this.$gettext(
          "Determine how much content the user can upload. Leave empty to use the default value of the instance."
        )
      }
    },
    allPermissions() {
      return [
        {
          code: "upload",
          label: this.$gettext("Upload")
        },
        {
          code: "library",
          label: this.$gettext("Library")
        },
        {
          code: "federation",
          label: this.$gettext("Federation")
        },
        {
          code: "settings",
          label: this.$gettext("Settings")
        }
      ]
    }
  },
  watch: {
    object() {
      this.$nextTick(() => {
        $("select.dropdown").dropdown()
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
