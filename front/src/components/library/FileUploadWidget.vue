<script>
import FileUpload from 'vue-upload-component'

export default {
  extends: FileUpload,
  methods: {
    uploadHtml5 (file) {
      let form = new window.FormData()
      let value
      for (let key in file.data) {
        value = file.data[key]
        if (value && typeof value === 'object' && typeof value.toString !== 'function') {
          if (value instanceof File) {
            form.append(key, value, value.name)
          } else {
            form.append(key, JSON.stringify(value))
          }
        } else if (value !== null && value !== undefined) {
          form.append(key, value)
        }
      }
      let filename = file.file.filename || file.name
      form.append('source', `upload://${filename}`)
      form.append(this.name, file.file, filename)
      let xhr = new XMLHttpRequest()
      xhr.open('POST', file.postAction)
      xhr.setRequestHeader('Authorization', this.$store.getters['auth/header'])
      return this.uploadXhr(xhr, file, form)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
