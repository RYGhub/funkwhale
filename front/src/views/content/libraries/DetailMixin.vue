<script>
import axios from 'axios'

export default {
  props: ['id'],
  created () {
    this.fetch()
  },
  data () {
    return {
      isLoadingLibrary: false,
      library: null
    }
  },
  methods: {
    fetch () {
      let self = this
      self.isLoadingLibrary = true
      axios.get(`libraries/${this.id}/`).then((response) => {
        self.library = response.data
        self.isLoadingLibrary = false
      })
    }
  }
}
</script>
