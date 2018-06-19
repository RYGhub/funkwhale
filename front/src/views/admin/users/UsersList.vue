<template>
  <div v-title="$t('Users')">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">{{ $t('Users') }}</h2>
      <div class="ui hidden divider"></div>
      <users-table></users-table>
    </div>
  </div>
</template>

<script>
import UsersTable from '@/components/manage/users/UsersTable'

export default {
  components: {
    UsersTable
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
