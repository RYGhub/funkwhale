<template>
  <div class="ui playlist card">
    <div class="ui top attached icon button" :style="coversStyle">
    </div>
    <div class="content">
      <div class="header">
        <div class="right floated">
          <play-button
            :is-playable="playlist.is_playable"
            :icon-only="true" class="ui inline"
            :button-classes="['ui', 'circular', 'large', {orange: playlist.tracks_count > 0}, 'icon', 'button', {disabled: playlist.tracks_count === 0}]"
            :playlist="playlist"></play-button>
          <play-button
            :is-playable="playlist.is_playable"
            class="basic inline icon"
            :dropdown-only="true"
            :dropdown-icon-classes="['ellipsis', 'vertical', 'large', {disabled: playlist.tracks_count === 0}, 'grey']"
            :account="playlist.actor"
            :playlist="playlist"></play-button>
        </div>
        <router-link :title="playlist.name" class="discrete link" :to="{name: 'library.playlists.detail', params: {id: playlist.id }}">
          {{ playlist.name | truncate(30) }}
        </router-link>
      </div>
      <div class="meta">
        <duration :seconds="playlist.duration" />
         |
        <i class="sound icon"></i>
        <translate translate-context="Content/*/Card/List item"
          translate-plural="%{ count } tracks"
          :translate-n="playlist.tracks_count"
          :translate-params="{count: playlist.tracks_count}">
          %{ count} track
        </translate>&nbsp;
      </div>
    </div>
    <div class="extra content">
      <user-link :user="playlist.user" class="left floated" />
      <span class="right floated">
        <i class="clock outline icon" />
        <human-date :date="playlist.creation_date" />
      </span>
    </div>
  </div>
</template>

<script>
import PlayButton from '@/components/audio/PlayButton'

export default {
  props: ['playlist'],
  components: {
    PlayButton
  },
  computed: {
    coversStyle () {
      let self = this
      let urls = this.playlist.album_covers.map((url) => {
        url = self.$store.getters['instance/absoluteUrl'](url)
        return `url("${url}")`
      }).slice(0, 4)
      return {
        'background-image': urls.join(', ')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.playlist.card .header .ellipsis.vertical.large.grey {
  font-size: 1.2em;
  margin-right: 0;
}
</style>
<style scoped>
.card .header {
  margin-bottom: 0.25em;
}

.attached.button {
  background-size: 25%;
  background-repeat: no-repeat;
  background-origin: border-box;
  background-position: 0 0, 33.33% 0, 66.67% 0, 100% 0;
  /* background-position: 0 0, 50% 0, 100% 0; */
  /* background-position: 0 0, 25% 0, 50% 0, 75% 0, 100% 0; */
  font-size: 4em;
  box-shadow: 0px 0px 0px 1px rgba(34, 36, 38, 0.15) inset !important;
  padding: unset;
}
</style>
