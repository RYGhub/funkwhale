<template>

  <section class="ui vertical stripe segment">
    <div class="ui text container">
      <h2>
        <translate v-if="canEdit" key="1" translate-context="Content/*/Title">Edit this track</translate>
        <translate v-else key="2" translate-context="Content/*/Title">Suggest an edit on this track</translate>
      </h2>
      <edit-form
        v-if="!isLoadingLicenses"
        :object-type="objectType"
        :object="object"
        :can-edit="canEdit"
        :licenses="licenses"></edit-form>
      </div>
    </section>
</template>

<script>
import axios from "axios"

import EditForm from '@/components/library/EditForm'
export default {
  props: ["objectType", "object", "libraries"],
  data() {
    return {
      id: this.object.id,
      isLoadingLicenses: false,
      licenses: []
    }
  },
  components: {
    EditForm
  },
  created () {
    this.fetchLicenses()
  },
  methods: {
    fetchLicenses () {
      let self = this
      self.isLoadingLicenses = true
      axios.get('licenses/').then((response) => {
        self.isLoadingLicenses = false
        self.licenses = response.data.results
      })
    }
  },
  computed: {
    canEdit () {
      return true
    }
  }
}
</script>
