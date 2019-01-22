<template>
  <main v-title="labels.domains">
    <section class="ui vertical stripe segment">
      <h2 class="ui left floated header"><translate>Domains</translate></h2>
      <form class="ui right floated form" @submit.prevent="createDomain">
        <div v-if="errors && errors.length > 0" class="ui negative message">
          <div class="header"><translate>Error while creating domain</translate></div>
          <ul class="list">
            <li v-for="error in errors">{{ error }}</li>
          </ul>
        </div>
        <div class="inline fields">
          <div class="field">
            <label for="domain"><translate>Add a domain</translate></label>
            <input type="text" id="domain" v-model="domainName">
          </div>
          <div class="field">
            <button :class="['ui', {'loading': isCreating}, 'green', 'button']" type="submit" :disabled="isCreating">
              <label for="domain"><translate>Add</translate></label>
            </button>
          </div>
        </div>
      </form>
      <div class="ui clearing hidden divider"></div>
      <domains-table></domains-table>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

import DomainsTable from "@/components/manage/moderation/DomainsTable"
export default {
  components: {
    DomainsTable
  },
  data () {
    return {
      domainName: '',
      isCreating: false,
      errors: []
    }
  },
  computed: {
    labels() {
      return {
        domains: this.$gettext("Domains")
      }
    }
  },
  methods: {
    createDomain () {
      let self = this
      this.isCreating = true
      this.errors = []
      axios.post('manage/federation/domains/', {name: this.domainName}).then((response) => {
        this.isCreating = false
        this.$router.push({
          name: "manage.moderation.domains.detail",
          params: {'id': response.data.name}
        })
      }, (error) => {
        self.isCreating = false
        self.errors = error.backendErrors
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
