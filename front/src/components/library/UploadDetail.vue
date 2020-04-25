<template>
  <main>
    <div v-if="isLoading" class="ui vertical segment">
      <div class="ui centered active inline loader"></div>
    </div>
  </main>
</template>

<script>
import axios from "axios"


export default {
  props: ["id"],
  async created() {
    let upload = await this.fetchData()
    this.$router.replace({name: "library.tracks.detail", params: {id: upload.track.id}})
  },
  methods: {
    async fetchData() {
      this.isLoading = true
      let response = await axios.get(`uploads/${this.id}/`, {params: {refresh: 'true', include_channels: 'true'}})
      this.isLoading = false
      return response.data
    },
  }
}
</script>
