<template>
<div :class="['ui', 'vertical', 'left', 'visible', 'wide', {'collapsed': isCollapsed}, 'sidebar',]">
  <div class="ui inverted segment header-wrapper">
    <search-bar @search="isCollapsed = false">
      <router-link :title="'Funkwhale'" :to="{name: 'index'}">
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
      <a class="active item" data-tab="library">Browse</a>
      <a class="item" data-tab="queue">
        Queue &nbsp;
         <template v-if="queue.tracks.length === 0">
           (empty)
         </template>
         <template v-else>
           ({{ queue.currentIndex + 1}} of {{ queue.tracks.length }})
         </template>
      </a>
    </div>
  </div>
  <div class="tabs">
    <div class="ui bottom attached active tab" data-tab="library">
      <div class="ui inverted vertical fluid menu">
        <router-link class="item" v-if="$store.state.auth.authenticated" :to="{name: 'profile', params: {username: $store.state.auth.username}}"><i class="user icon"></i> Logged in as {{ $store.state.auth.username }}</router-link>
        <router-link class="item" v-if="$store.state.auth.authenticated" :to="{name: 'logout'}"><i class="sign out icon"></i> Logout</router-link>
        <router-link class="item" v-else :to="{name: 'login'}"><i class="sign in icon"></i> Login</router-link>
        <router-link class="item" :to="{path: '/library'}"><i class="sound icon"> </i>Browse library</router-link>
        <router-link class="item" :to="{path: '/favorites'}"><i class="heart icon"></i> Favorites</router-link>
        <router-link
          v-if="$store.state.auth.authenticated"
          class="item" :to="{path: '/activity'}"><i class="bell icon"></i> Activity</router-link>
      </div>
    </div>
    <div v-if="queue.previousQueue " class="ui black icon message">
      <i class="history icon"></i>
      <div class="content">
        <div class="header">
          Do you want to restore your previous queue?
        </div>
        <p>{{ queue.previousQueue.tracks.length }} tracks</p>
        <div class="ui two buttons">
          <div @click="queue.restore()" class="ui basic inverted green button">Yes</div>
          <div @click="queue.removePrevious()" class="ui basic inverted red button">No</div>
        </div>
      </div>
    </div>
    <div class="ui bottom attached tab" data-tab="queue">
      <table class="ui compact inverted very basic fixed single line unstackable table">
        <draggable v-model="queue.tracks" element="tbody" @update="reorder">
          <tr @click="$store.dispatch('queue/currentIndex', index)" v-for="(track, index) in queue.tracks" :key="index" :class="[{'active': index === queue.currentIndex}]">
              <td class="right aligned">{{ index + 1}}</td>
              <td class="center aligned">
                  <img class="ui mini image" v-if="track.album.cover" :src="backend.absoluteUrl(track.album.cover)">
                  <img class="ui mini image" v-else src="../assets/audio/default-cover.png">
              </td>
              <td colspan="4">
                  <strong>{{ track.title }}</strong><br />
                  {{ track.artist.name }}
              </td>
              <td>
                <template v-if="$store.getters['favorites/isFavorite'](track.id)">
                  <i class="pink heart icon"></i>
                </template>
              </td>
              <td>
                  <i @click.stop="cleanTrack(index)" class="circular trash icon"></i>
              </td>
            </tr>
          </draggable>
      </table>
      <div v-if="$store.state.radios.running" class="ui black message">

        <div class="content">
          <div class="header">
            <i class="feed icon"></i> You have a radio playing
          </div>
          <p>New tracks will be appended here automatically.</p>
          <div @click="$store.dispatch('radios/stop')" class="ui basic inverted red button">Stop radio</div>
        </div>
      </div>
    </div>
  </div>
  <player></player>
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
      backend: backend,
      isCollapsed: true
    }
  },
  mounted () {
    $(this.$el).find('.menu .item').tab()
  },
  computed: {
    ...mapState({
      queue: state => state.queue,
      url: state => state.route.path
    })
  },
  methods: {
    ...mapActions({
      cleanTrack: 'queue/cleanTrack'
    }),
    reorder: function (oldValue, newValue) {
      this.$store.commit('queue/reorder', {oldValue, newValue})
    }
  },
  watch: {
    url: function () {
      this.isCollapsed = true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import '../style/vendor/media';

$sidebar-color: #3D3E3F;

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
.tabs {
  overflow-y: auto;
  @include media(">tablet") {
    height: 0px;
  }
  @include media("<desktop") {
    max-height: 400px;
  }
}
.tab[data-tab="queue"] {
  tr {
    cursor: pointer;
  }
}
.sidebar .segment {
  margin: 0;
  border-radius: 0;
}

.ui.inverted.segment.header-wrapper {
  padding: 0;
}
.tabs {
  flex: 1;
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
</style>
