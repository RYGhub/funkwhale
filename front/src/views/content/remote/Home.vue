<template>
  <div class="ui vertical aligned stripe segment">
    <div v-if="isLoading" :class="['ui', {'active': isLoading}, 'inverted', 'dimmer']">
      <div class="ui text loader"><translate>Loading remote libraries...</translate></div>
    </div>
    <div v-else class="ui text container">
      <h1 class="ui header"><translate>Remote libraries</translate></h1>
      <p><translate>Remote libraries are owned by other users on the network. You can access them as long as they are public or you are granted access.</translate></p>
      <scan-form @scanned="scanResult = $event"></scan-form>
      <div class="ui hidden divider"></div>
      <div v-if="scanResult && scanResult.results.length > 0" class="ui two cards">
        <library-card :library="library" v-for="library in scanResult.results" :key="library.fid" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ScanForm from './ScanForm'
import LibraryCard from './Card'

export default {
  data () {
    return {
      isLoading: false,
      scanResult: null
    }
  },
  created () {
    // this.fetch()
  },
  components: {
    ScanForm,
    LibraryCard
  },
  methods: {
    fetch () {
      this.isLoading = true
      let self = this
      axios.get('libraries/').then((response) => {
        self.isLoading = false
        self.libraries = response.data.results
        if (self.libraries.length === 0) {
          self.hiddenForm = false
        }
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
