<template>
  <div class="main pusher" v-title="'Welcome'">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
          {{ $gettext('Welcome on Funkwhale') }}
        </h1>
        <p>{{ $gettext('We think listening to music should be simple.') }}</p>
        <router-link class="ui icon button" to="/about">
          <i class="info icon"></i>
          {{ $gettext('Learn more about this instance') }}
        </router-link>
        <router-link class="ui icon teal button" to="/library">
          {{ $gettext('Get me to the library') }}
          <i class="right arrow icon"></i>
        </router-link>
      </div>
    </div>
    <div class="ui vertical stripe segment">
      <div class="ui middle aligned stackable text container">
        <div class="ui grid">
          <div class="row">
            <div class="eight wide left floated column">
              <h2 class="ui header">
                {{ $gettext('Why funkwhale?') }}
              </h2>
              <p>{{ $gettext('That\'s simple: we loved Grooveshark and we want to build something even better.') }}</p>
            </div>
            <div class="four wide left floated column">
              <img class="ui medium image" src="../assets/logo/logo.png" />
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          {{ $gettext('Unlimited music') }}
        </h2>
        <p>{{ $gettext('Funkwhale is designed to make it easy to listen to music you like, or to discover new artists.') }}</p>
        <div class="ui list">
          <div class="item">
            <i class="sound icon"></i>
            <div class="content">
              {{ $gettext('Click once, listen for hours using built-in radios') }}
            </div>
          </div>
          <div class="item">
            <i class="heart icon"></i>
            <div class="content">
              {{ $gettext('Keep a track of your favorite songs') }}
            </div>
          </div>
          <div class="item">
            <i class="list icon"></i>
            <div class="content">
              {{ $gettext('Playlists? We got them') }}
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          {{ $gettext('Clean library') }}
        </h2>
        <p>{{ $gettext('Funkwhale takes care of handling your music') }}.</p>
        <div class="ui list">
          <div class="item">
            <i class="download icon"></i>
            <div class="content">
              {{ $gettext('Import music from various platforms, such as YouTube or SoundCloud') }}
            </div>
          </div>
          <div class="item">
            <i class="tag icon"></i>
            <div class="content">
              <template v-translate>
                Get quality metadata about your music thanks to
                <a href="https://musicbrainz.org" target="_blank">
                  MusicBrainz
                </a>
              </template>
            </div>
          </div>
          <div class="item">
            <i class="plus icon"></i>
            <div class="content">
              {{ $gettext('Covers, lyrics, our goal is to have them all ;)') }}
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          {{ $gettext('Easy to use') }}
        </h2>
        <p>{{ $gettext('Funkwhale is dead simple to use.') }}</p>
        <div class="ui list">
          <div class="item">
            <i class="book icon"></i>
            <div class="content">
              {{ $gettext('No add-ons, no plugins : you only need a web library') }}
            </div>
          </div>
          <div class="item">
            <i class="wizard icon"></i>
            <div class="content">
              {{ $gettext('Access your music from a clean interface that focus on what really matters') }}
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          {{ $gettext('Your music, your way') }}
        </h2>
        <p>{{ $gettext('Funkwhale is free and gives you control on your music.') }}</p>
        <div class="ui list">
          <div class="item">
            <i class="smile icon"></i>
            <div class="content">
              {{ $gettext('The plaform is free and open-source, you can install it and modify it without worries') }}
            </div>
          </div>
          <div class="item">
            <i class="protect icon"></i>
            <div class="content">
              {{ $gettext('We do not track you or bother you with ads') }}
            </div>
          </div>
          <div class="item">
            <i class="users icon"></i>
            <div class="content">
              {{ $gettext('You can invite friends and family to your instance so they can enjoy your music') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'home',
  data () {
    return {}
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.stripe p {
  font-size: 120%;
}
.list.icon {
  padding: 0;
}
</style>
