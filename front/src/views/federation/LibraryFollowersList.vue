<template>
  <div v-title="'Followers'">
    <div class="ui vertical stripe segment">
      <h2 class="ui header">{{ $t('Browsing followers') }}</h2>
      <p>
        {{ $t('Be careful when accepting follow requests, as it means the follower will have access to your entire library.') }}
      </p>
      <div class="ui hidden divider"></div>
      <library-follow-table></library-follow-table>
    </div>
  </div>
</template>

<script>
import LibraryFollowTable from '@/components/federation/LibraryFollowTable'

export default {
  components: {
    LibraryFollowTable
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
