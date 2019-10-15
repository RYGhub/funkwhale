<template>
  <div class="ui placeholder segment">
    <div class="ui icon header">
      <i class="list icon"></i>
      <translate translate-context="Content/Home/Placeholder">
        No playlists have been created yet
      </translate>
    </div>
    <button
      @click="$store.commit('playlists/chooseTrack', null)"
      class="ui primary button"
      >
      <translate translate-context="Content/Home/CreatePlaylist">
        Create Playlist
      </translate>
    </button>
  </div>
</template>
