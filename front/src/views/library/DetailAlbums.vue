<template>
  <section>
    <album-widget
      :key="String(object.uploads_count)"
      :header="false"
      :search="true"
      :controls="false"
      :filters="{playable: true, ordering: '-creation_date', library: object.uuid}">
      <empty-state slot="empty-state">
        <p>
          <translate key="1" v-if="isOwner" translate-context="*/*/*">This library is empty, you should upload something in it!</translate>
          <translate key="2" v-else translate-context="*/*/*">You may need to follow this library to see its content.</translate>
        </p>
      </empty-state>
    </album-widget>
  </section>
</template>

<script>
import AlbumWidget from "@/components/audio/album/Widget"

export default {
  props: ['object', 'isOwner'],
  components: {
    AlbumWidget,
  },
}
</script>
