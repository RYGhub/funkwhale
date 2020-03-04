<template>
  <section>
    <template v-if="$store.getters['ui/layoutVersion'] === 'small'">
      <rendered-description
        :content="object.description ? {html: object.description} : null"
        :update-url="`channels/${object.uuid}/`"
        :can-update="false"></rendered-description>
        <div class="ui hidden divider"></div>
    </template>
    <artist-widget
      :key="object.uploads_count"
      ref="artists"
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
    </artist-widget>
  </section>
</template>

<script>
import ArtistWidget from "@/components/audio/artist/Widget"

export default {
  props: ['object', 'isOwner'],
  components: {
    ArtistWidget,
  },
  data () {
    return  {
      query: ''
    }
  }
}
</script>
