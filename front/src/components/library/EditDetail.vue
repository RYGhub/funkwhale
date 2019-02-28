<template>

  <section :class="['ui', 'vertical', 'stripe', {loading: isLoading}, 'segment']">
    <div class="ui text container">
      <edit-card v-if="obj" :obj="obj" :current-state="currentState" />
    </div>
  </section>
</template>

<script>
import axios from "axios"
import edits from '@/edits'
import EditCard from '@/components/library/EditCard'
export default {
  props: ["object", "objectType", "editId"],
  components: {
    EditCard
  },
  data () {
    return {
      isLoading: true,
      obj: null,
    }
  },
  created () {
    this.fetchData()
  },
  computed: {
    configs: edits.getConfigs,
    config: edits.getConfig,
    currentState: edits.getCurrentState,
    currentState () {
      let self = this
      let s = {}
      this.config.fields.forEach(f => {
        s[f.id] = {value: f.getValue(self.object)}
      })
      return s
    }
  },
  methods: {
    fetchData () {
      var self = this
      this.isLoading = true
      axios.get(`mutations/${this.editId}/`).then(response => {
        self.obj = response.data
        self.isLoading = false
      })
    }
  }
}
</script>
