<template>
  <div v-title="$gettext('Invitations')">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">{{ $gettext('Invitations') }}</h2>
      <invitation-form></invitation-form>
      <div class="ui hidden divider"></div>
      <invitations-table></invitations-table>
    </div>
  </div>
</template>

<script>
import InvitationForm from '@/components/manage/users/InvitationForm'
import InvitationsTable from '@/components/manage/users/InvitationsTable'

export default {
  components: {
    InvitationForm,
    InvitationsTable
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
