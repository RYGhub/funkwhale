<template>
  <div class="ui card">
    <div class="content">
      <div class="header">
        <router-link class="discrete link" :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">
          {{ playlist.name }}
        </router-link>
      </div>
      <div class="meta">
        <i class="user icon"></i> {{ playlist.user.username }}
      </div>
      <div class="meta">
        <i class="clock icon"></i>
        <i18next path="Updated {%date%}">
          <human-date :date="playlist.modification_date" />
        </i18next>
      </div>
    </div>
    <div class="extra content">
      <span>
        <i class="sound icon"></i>
        {{ $t('{%count%} tracks', { count: playlist.tracks_count }) }}
      </span>
      <play-button class="mini basic orange right floated" :playlist="playlist">Play all</play-button>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['playlist'],
  components: {
    PlayButton
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
