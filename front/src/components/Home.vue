<template>
  <div class="main pusher" v-title="labels.title">
    <div class="ui vertical center aligned stripe segment">
      <div class="ui text container">
        <h1 class="ui huge header">
          <translate>Welcome on Funkwhale</translate>
        </h1>
        <p><translate>We think listening to music should be simple.</translate></p>
        <router-link class="ui icon button" to="/about">
          <i class="info icon"></i>
          <translate>Learn more about this instance</translate>
        </router-link>
        <router-link class="ui icon teal button" to="/library">
          <translate>Get me to the library</translate>
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
                <translate>Why funkwhale?</translate>
              </h2>
              <p><translate>That's simple: we loved Grooveshark and we want to build something even better.</translate></p>
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
          <translate>Unlimited music</translate>
        </h2>
        <p><translate>Funkwhale is designed to make it easy to listen to music you like, or to discover new artists.</translate></p>
        <div class="ui list">
          <div class="item">
            <i class="sound icon"></i>
            <div class="content">
              <translate>Click once, listen for hours using built-in radios</translate>
            </div>
          </div>
          <div class="item">
            <i class="heart icon"></i>
            <div class="content">
              <translate>Keep a track of your favorite songs</translate>
            </div>
          </div>
          <div class="item">
            <i class="list icon"></i>
            <div class="content">
              <translate>Playlists? We got them</translate>
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          <translate>Clean library</translate>
        </h2>
        <p><translate>Funkwhale takes care of handling your music</translate>.</p>
        <div class="ui list">
          <div class="item">
            <i class="download icon"></i>
            <div class="content">
              <translate>Import music from various platforms, such as YouTube or SoundCloud</translate>
            </div>
          </div>
          <div class="item">
            <i class="tag icon"></i>
            <div
              class="content"
              v-translate="{url: musicbrainzUrl}">
                Get quality metadata about your music thanks to <a href="%{ url }" target="_blank">MusicBrainz</a>
            </div>
          </div>
          <div class="item">
            <i class="plus icon"></i>
            <div class="content">
              <translate>Covers, lyrics, our goal is to have them all ;)</translate>
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          <translate>Easy to use</translate>
        </h2>
        <p><translate>Funkwhale is dead simple to use.</translate></p>
        <div class="ui list">
          <div class="item">
            <i class="book icon"></i>
            <div class="content">
              <translate>No add-ons, no plugins : you only need a web library</translate>
            </div>
          </div>
          <div class="item">
            <i class="wizard icon"></i>
            <div class="content">
              <translate>Access your music from a clean interface that focus on what really matters</translate>
            </div>
          </div>
        </div>
      </div>
      <div class="ui middle aligned stackable text container">
        <div class="ui hidden divider"></div>
        <h2 class="ui header">
          <translate>Your music, your way</translate>
        </h2>
        <p><translate>Funkwhale is free and gives you control on your music.</translate></p>
        <div class="ui list">
          <div class="item">
            <i class="smile icon"></i>
            <div class="content">
              <translate>The plaform is free and open-source, you can install it and modify it without worries</translate>
            </div>
          </div>
          <div class="item">
            <i class="protect icon"></i>
            <div class="content">
              <translate>We do not track you or bother you with ads</translate>
            </div>
          </div>
          <div class="item">
            <i class="users icon"></i>
            <div class="content">
              <translate>You can invite friends and family to your instance so they can enjoy your music</translate>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data () {
    return {
      musicbrainzUrl: 'https://musicbrainz.org/'
    }
  },
  computed: {
    labels () {
      return {
        title: this.$gettext('Welcome')
      }
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
