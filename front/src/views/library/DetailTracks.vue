<template>
  <section>
    <track-table
      :key="object.uploads_count"
      :display-actions="false"
      :search="true"
      :filters="{playable: true, library: object.uuid, ordering: '-creation_date'}">
      <empty-state slot="empty-state">
        <p>
          <translate key="1" v-if="isOwner" translate-context="*/*/*">This library is empty, you should upload something in it!</translate>
          <translate key="2" v-else translate-context="*/*/*">You may need to follow this library to see its content.</translate>
        </p>
      </empty-state>
    </track-table>
  </section>
</template>

<script>
import TrackTable from '@/components/audio/track/Table'

export default {
  props: ['object', 'isOwner'],
  components: {
    TrackTable,
  },
}
</script>
