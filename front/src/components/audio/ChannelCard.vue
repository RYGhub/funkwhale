<template>
  <div class="card app-card">
    <div
      @click="$router.push({name: 'channels.detail', params: {id: object.uuid}})"
      :class="['ui', 'head-image', 'padded image', {'default-cover': !object.artist.cover}]" v-lazy:background-image="imageUrl">
      <play-button :icon-only="true" :is-playable="true" :button-classes="['ui', 'circular', 'large', 'orange', 'icon', 'button']" :artist="object.artist"></play-button>
    </div>
    <div class="content">
      <strong>
        <router-link class="discrete link" :title="object.artist.name" :to="{name: 'channels.detail', params: {id: object.uuid}}">
          {{ object.artist.name }}
        </router-link>
      </strong>
      <div class="description">
        <tags-list label-classes="tiny" :truncate-size="20" :limit="2" :show-more="false" :tags="object.artist.tags"></tags-list>
      </div>
    </div>
    <div class="extra content">
      <translate translate-context="Content/Channel/Paragraph"
        translate-plural="%{ count } episodes"
        :translate-n="object.artist.tracks_count"
        :translate-params="{count: object.artist.tracks_count}">
        %{ count } episode
      </translate>
      <play-button class="right floated basic icon" :dropdown-only="true" :is-playable="true" :dropdown-icon-classes="['ellipsis', 'horizontal', 'large', 'grey']" :artist="object.artist"></play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'
import TagsList from "@/components/tags/List"

export default {
  props: {
    object: {type: Object},
  },
  components: {
    PlayButton,
    TagsList
  },
  computed: {
    imageUrl () {
      let url = '../../assets/audio/default-cover.png'

      if (this.object.artist.cover) {
        url = this.$store.getters['instance/absoluteUrl'](this.object.artist.cover.medium_square_crop)
      } else {
        return null
      }
      return url
    }
  }
}
</script>
