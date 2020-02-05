<template>
  <section>
    <channel-entries :filters="{channel: object.uuid, ordering: '-creation_date', playable: 'true'}">
      <h2 class="ui header">
        <translate translate-context="Content/Channel/Paragraph">Latest episodes</translate>
      </h2>
    </channel-entries>
    <div class="ui hidden divider"></div>
    <channel-series :filters="{channel: object.uuid, ordering: '-creation_date', playable: 'true'}">
      <h2 class="ui header">
        <translate translate-context="Content/Channel/Paragraph">Series</translate>
      </h2>
    </channel-series>
  </section>
</template>

<script>
import ChannelEntries from "@/components/audio/ChannelEntries"
import ChannelSeries from "@/components/audio/ChannelSeries"


export default {
  props: ['object'],
  components: {
    ChannelEntries,
    ChannelSeries,
  },
}
</script>
