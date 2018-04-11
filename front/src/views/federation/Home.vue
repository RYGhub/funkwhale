<template>
  <div class="main pusher" v-title="'Federation'">
    <div class="ui vertical stripe segment">
      <h1 class="ui header">Manage federation</h1>
      <library-form @scanned="updateLibraryData"></library-form>
      <library-card v-if="libraryData" :library-data="libraryData"></library-card>
    </div>
    <div class="ui vertical stripe segment">
    </div>
  </div>
</template>

<script>
// import axios from 'axios'
import TrackTable from '@/components/audio/track/Table'
import RadioButton from '@/components/radios/Button'
import Pagination from '@/components/Pagination'
import LibraryForm from '@/components/federation/LibraryForm'
import LibraryCard from '@/components/federation/LibraryCard'

export default {
  components: {
    TrackTable,
    RadioButton,
    Pagination,
    LibraryForm,
    LibraryCard
  },
  data () {
    return {
      libraryData: null
    }
  },
  methods: {
    updateLibraryData (data) {
      this.libraryData = data
    }
  }
}
</script>
