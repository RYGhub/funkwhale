<template>
  <div class="main pusher">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
            Welcome on funkwhale
        </h1>
        <p>We think listening music should be simple.</p>
        <router-link class="ui icon teal button" to="/browse">
          Get me to the library
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
                Why funkwhale?
              </h2>
              <p>That's simple: we loved Grooveshark and we want to build something even better.</p>
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
          Unlimited music
        </h2>
        <p>Funkwhale is designed to make it easy to listen to music you like, or to discover new artists.</p>
        <div class="ui list">
          <div class="item">
            <i class="sound icon"></i>
            <div class="content">
              Click once, listen for hours using built-in radios
            </div>
          </div>
          <div class="item">
            <i class="heart icon"></i>
            <div class="content">
              Keep a track of your favorite songs
            </div>
          </div>
          <div class="item">
            <i class="list icon"></i>
            <div class="content">
              Playlists? We got them
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          Clean library
        </h2>
        <p>Funkwhale takes care of fealing your music.</p>
        <div class="ui list">
          <div class="item">
            <i class="download icon"></i>
            <div class="content">
              Import music from various platforms, such as YouTube or SoundCloud
            </div>
          </div>
          <div class="item">
            <i class="tag icon"></i>
            <div class="content">
              Get quality metadata about your music thanks to <a href="https://musicbrainz.org" target="_blank">MusicBrainz</a>
            </div>
          </div>
          <div class="item">
            <i class="plus icon"></i>
            <div class="content">
              Covers, lyrics, our goal is to have them all ;)
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          Easy to use
        </h2>
        <p>Funkwhale is dead simple to use.</p>
        <div class="ui list">
          <div class="item">
            <i class="browser icon"></i>
            <div class="content">
              No add-ons, no plugins : you only need a web browser
            </div>
          </div>
          <div class="item">
            <i class="wizard icon"></i>
            <div class="content">
              Access your music from a clean interface that focus on what really matters
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          Your music, your way
        </h2>
        <p>Funkwhale is free and gives you control on your music.</p>
        <div class="ui list">
          <div class="item">
            <i class="smile icon"></i>
            <div class="content">
              The plaform is free and open-source, you can install it and modify it without worries
            </div>
          </div>
          <div class="item">
            <i class="protect icon"></i>
            <div class="content">
              We do not track you or bother you with ads
            </div>
          </div>
          <div class="item">
            <i class="users icon"></i>
            <div class="content">
              You can invite friends and family to your instance so they can enjoy your music
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
    return {
      msg: 'Welcome to Your Vue.js App'
    }
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
