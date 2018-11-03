<template>
<div :class="['ui', 'vertical', 'left', 'visible', 'wide', {'collapsed': isCollapsed}, 'sidebar',]">
  <div class="ui inverted segment header-wrapper">
    <search-bar @search="isCollapsed = false">
      <router-link :title="'Funkwhale'" :to="{name: logoUrl}">
        <i class="logo bordered inverted orange big icon">
          <logo class="logo"></logo>
        </i>
      </router-link><span
        slot="after"
        @click="isCollapsed = !isCollapsed"
        :class="['ui', 'basic', 'big', {'inverted': isCollapsed}, 'orange', 'icon', 'collapse', 'button']">
          <i class="sidebar icon"></i></span>
    </search-bar>
  </div>

  <div class="menu-area">
    <div class="ui compact fluid two item inverted menu">
      <a class="active item" href @click.prevent.stop="selectedTab = 'library'" data-tab="library"><translate>Browse</translate></a>
      <a class="item" href @click.prevent.stop="selectedTab = 'queue'" data-tab="queue">
        <translate>Queue</translate>&nbsp;
         <template v-if="queue.tracks.length === 0">
           <translate>(empty)</translate>
         </template>
         <translate v-else :translate-params="{index: queue.currentIndex + 1, length: queue.tracks.length}">
          (%{ index } of %{ length })
         </translate>
      </a>
    </div>
  </div>
  <div class="tabs">
    <div class="ui bottom attached active tab" data-tab="library">
      <div class="ui inverted vertical large fluid menu">
        <div class="item">
          <div class="header"><translate>My account</translate></div>
          <div class="menu">
            <router-link class="item" v-if="$store.state.auth.authenticated" :to="{name: 'profile', params: {username: $store.state.auth.username}}">
              <i class="user icon"></i>
              <translate :translate-params="{username: $store.state.auth.username}">
                Logged in as %{ username }
              </translate>
              <img class="ui right floated circular tiny avatar image" v-if="$store.state.auth.profile.avatar.square_crop" :src="$store.getters['instance/absoluteUrl']($store.state.auth.profile.avatar.square_crop)" />
            </router-link>
            <router-link class="item" v-if="$store.state.auth.authenticated" :to="{path: '/settings'}"><i class="setting icon"></i><translate>Settings</translate></router-link>
            <router-link class="item" v-if="$store.state.auth.authenticated" :to="{name: 'notifications'}">
              <i class="feed icon"></i>
              <translate>Notifications</translate>
              <div
                v-if="$store.state.ui.notifications.inbox > 0"
                :class="['ui', 'teal', 'label']">
                {{ $store.state.ui.notifications.inbox }}</div>
            </router-link>
            <router-link class="item" v-if="$store.state.auth.authenticated" :to="{name: 'logout'}"><i class="sign out icon"></i><translate>Logout</translate></router-link>
            <template v-else>
              <router-link class="item" :to="{name: 'login'}"><i class="sign in icon"></i><translate>Login</translate></router-link>
              <router-link class="item" :to="{path: '/signup'}">
                <i class="corner add icon"></i>
                <translate>Create an account</translate>
              </router-link>
            </template>
          </div>
        </div>
        <div class="item">
          <div class="header"><translate>Music</translate></div>
          <div class="menu">
            <router-link class="item" :to="{path: '/library'}"><i class="sound icon"></i><translate>Browse library</translate></router-link>
            <router-link class="item" v-if="$store.state.auth.authenticated" :to="{path: '/favorites'}"><i class="heart icon"></i><translate>Favorites</translate></router-link>
            <a
              @click="$store.commit('playlists/chooseTrack', null)"
              v-if="$store.state.auth.authenticated"
              class="item">
              <i class="list icon"></i><translate>Playlists</translate>
            </a>
            <router-link
              v-if="$store.state.auth.authenticated"
              class="item" :to="{name: 'content.index'}"><i class="upload icon"></i><translate>Add content</translate></router-link>
          </div>
        </div>
        <div class="item" v-if="showAdmin">
          <div class="header"><translate>Administration</translate></div>
          <div class="menu">
            <router-link
              class="item"
              v-if="$store.state.auth.availablePermissions['settings']"
              :to="{path: '/manage/settings'}">
              <i class="settings icon"></i><translate>Settings</translate>
            </router-link>
            <router-link
              class="item"
              v-if="$store.state.auth.availablePermissions['settings']"
              :to="{name: 'manage.users.users.list'}">
              <i class="users icon"></i><translate>Users</translate>
            </router-link>
          </div>
        </div>
      </div>
    </div>
    <div v-if="queue.previousQueue " class="ui black icon message">
      <i class="history icon"></i>
      <div class="content">
        <div class="header">
          <translate>Do you want to restore your previous queue?</translate>
        </div>
        <p>
          <translate
            translate-plural="%{ count } tracks"
            :translate-n="queue.previousQueue.tracks.length"
            :translate-params="{count: queue.previousQueue.tracks.length}">
            %{ count } track
          </translate>
        </p>
        <div class="ui two buttons">
          <div @click="queue.restore()" class="ui basic inverted green button"><translate>Yes</translate></div>
          <div @click="queue.removePrevious()" class="ui basic inverted red button"><translate>No</translate></div>
        </div>
      </div>
    </div>
    <div class="ui bottom attached tab" data-tab="queue">
      <table class="ui compact inverted very basic fixed single line unstackable table">
        <draggable v-model="tracks" element="tbody" @update="reorder">
          <tr @click="$store.dispatch('queue/currentIndex', index)" v-for="(track, index) in tracks" :key="index" :class="[{'active': index === queue.currentIndex}]">
              <td class="right aligned">{{ index + 1}}</td>
              <td class="center aligned">
                  <img class="ui mini image" v-if="track.album.cover && track.album.cover.original" :src="$store.getters['instance/absoluteUrl'](track.album.cover.small_square_crop)">
                  <img class="ui mini image" v-else src="../assets/audio/default-cover.png">
              </td>
              <td colspan="4">
                  <button class="title reset ellipsis">
                    <strong>{{ track.title }}</strong><br />
                    {{ track.artist.name }}
                  </button>
              </td>
              <td>
                <template v-if="$store.getters['favorites/isFavorite'](track.id)">
                  <i class="pink heart icon"></i>
                </template>
              </td>
              <td>
                  <button @click.stop="cleanTrack(index)" :class="['ui', {'inverted': index != queue.currentIndex}, 'really', 'tiny', 'basic', 'circular', 'icon', 'button']">
                    <i class="trash icon"></i>
                  </button>
              </td>
            </tr>
          </draggable>
      </table>
      <div v-if="$store.state.radios.running" class="ui black message">
        <div class="content">
          <div class="header">
            <i class="feed icon"></i> <translate>You have a radio playing</translate>
          </div>
          <p><translate>New tracks will be appended here automatically.</translate></p>
          <div @click="$store.dispatch('radios/stop')" class="ui basic inverted red button"><translate>Stop radio</translate></div>
        </div>
      </div>
    </div>
  </div>
  <player @next="scrollToCurrent" @previous="scrollToCurrent"></player>
</div>
</template>

<script>
import {mapState, mapActions} from 'vuex'

import Player from '@/components/audio/Player'
import Logo from '@/components/Logo'
import SearchBar from '@/components/audio/SearchBar'
import backend from '@/audio/backend'
import draggable from 'vuedraggable'

import $ from 'jquery'

export default {
  name: 'sidebar',
  components: {
    Player,
    SearchBar,
    Logo,
    draggable
  },
  data () {
    return {
      selectedTab: 'library',
      backend: backend,
      tracksChangeBuffer: null,
      isCollapsed: true,
      fetchInterval: null,
      showAdmin: this.getShowAdmin()
    }
  },
  mounted () {
    $(this.$el).find('.menu .item').tab()
  },
  destroy () {
    if (this.fetchInterval) {
      clearInterval(this.fetchInterval)
    }
  },
  computed: {
    ...mapState({
      queue: state => state.queue,
      url: state => state.route.path
    }),
    labels () {
      let pendingRequests = this.$gettext('Pending import requests')
      let pendingFollows = this.$gettext('Pending follow requests')
      return {
        pendingRequests,
        pendingFollows
      }
    },
    tracks: {
      get () {
        return this.$store.state.queue.tracks
      },
      set (value) {
        this.tracksChangeBuffer = value
      }
    },
    logoUrl () {
      if (this.$store.state.auth.authenticated) {
        return 'library.index'
      } else {
        return 'index'
      }
    }
  },
  methods: {
    ...mapActions({
      cleanTrack: 'queue/cleanTrack'
    }),
    getShowAdmin () {
      let adminPermissions = [
        this.$store.state.auth.availablePermissions['federation'],
        this.$store.state.auth.availablePermissions['library'],
        this.$store.state.auth.availablePermissions['upload']
      ]
      return adminPermissions.filter(e => {
        return e
      }).length > 0
    },
    reorder: function (event) {
      this.$store.commit('queue/reorder', {
        tracks: this.tracksChangeBuffer, oldIndex: event.oldIndex, newIndex: event.newIndex})
    },
    scrollToCurrent () {
      let current = $(this.$el).find('[data-tab="queue"] .active')[0]
      if (!current) {
        return
      }
      let container = $(this.$el).find('.tabs')[0]
      // Position container at the top line then scroll current into view
      container.scrollTop = 0
      current.scrollIntoView(true)
      // Scroll back nothing if element is at bottom of container else do it
      // for half the height of the containers display area
      var scrollBack = (container.scrollHeight - container.scrollTop <= container.clientHeight) ? 0 : container.clientHeight / 2
      container.scrollTop = container.scrollTop - scrollBack
    }
  },
  watch: {
    url: function () {
      this.isCollapsed = true
    },
    selectedTab: function (newValue) {
      if (newValue === 'queue') {
        this.scrollToCurrent()
      }
    },
    '$store.state.queue.currentIndex': function () {
      if (this.selectedTab !== 'queue') {
        this.scrollToCurrent()
      }
    },
    '$store.state.auth.availablePermissions': {
      handler () {
        this.showAdmin = this.getShowAdmin()
      },
      deep: true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import '../style/vendor/media';

$sidebar-color: #3d3e3f;

.sidebar {
	background: $sidebar-color;
  @include media(">tablet") {
    display:flex;
    flex-direction:column;
    justify-content: space-between;
  }
  @include media(">desktop") {
    .collapse.button {
      display: none !important;
    }
  }
  @include media("<desktop") {
    position: static !important;
    width: 100% !important;
    &.collapsed {
      .menu-area, .player-wrapper, .tabs {
        display: none;
      }
    }
  }

  > div {
    margin: 0;
    background-color: $sidebar-color;
  }
  .menu.vertical {
    background: $sidebar-color;
  }
}

.menu-area {
  .menu .item:not(.active):not(:hover) {
    opacity: 0.75;
  }

  .menu .item {
    border-radius: 0;
  }

  .menu .item.active {
    background-color: $sidebar-color;
    &:hover {
      background-color: rgba(255, 255, 255, 0.06);
    }
  }
}
.vertical.menu {
  .item .item {
    font-size: 1em;
    > i.icon {
      float: none;
      margin: 0 0.5em 0 0;
    }
    &:not(.active) {
      color: rgba(255, 255, 255, 0.75);
    }
  }
}
.tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  justify-content: space-between;
  @include media("<desktop") {
    max-height: 500px;
  }
}
.ui.tab.active {
  display: flex;
}
.tab[data-tab="queue"] {
  flex-direction: column;
  tr {
    cursor: pointer;
  }
  td:nth-child(2) {
    width: 55px;
  }
}
.tab[data-tab="library"] {
  flex-direction: column;
  flex: 1 1 auto;
  > .menu {
    flex: 1;
    flex-grow: 1;
  }
  > .player-wrapper {
    width: 100%;
  }
}
.sidebar .segment {
  margin: 0;
  border-radius: 0;
}

.ui.inverted.segment.header-wrapper {
  padding: 0;
}

.logo {
  cursor: pointer;
  display: inline-block;
  margin: 0px;
}

.ui.search {
  display: flex;

  .collapse.button, .collapse.button:hover, .collapse.button:active {
    box-shadow: none !important;
    margin: 0px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.ui.message.black {
  background: $sidebar-color;
}

.ui.mini.image {
  width: 100%;
}
</style>

<style lang="scss">
.sidebar {
  .ui.search .input {
    flex: 1;
    .prompt {
      border-radius: 0;
    }
  }
}
.ui.tiny.avatar.image {
  position: relative;
  top: -0.5em;
  width: 3em;
}

:not(.active) button.title {
  outline-color: white;
}
</style>
