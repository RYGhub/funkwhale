import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/auth/Login'
import Profile from '@/components/auth/Profile'
import Logout from '@/components/auth/Logout'
import Browse from '@/components/browse/Browse'
import BrowseHome from '@/components/browse/Home'
import BrowseArtist from '@/components/browse/Artist'
import BrowseAlbum from '@/components/browse/Album'
import BrowseTrack from '@/components/browse/Track'
import Favorites from '@/components/favorites/List'

Vue.use(Router)

export default new Router({
  mode: 'history',
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'index',
      component: Home
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/logout',
      name: 'logout',
      component: Logout
    },
    {
      path: '/@:username',
      name: 'profile',
      component: Profile,
      props: true
    },
    {
      path: '/favorites',
      component: Favorites
    },
    {
      path: '/browse',
      component: Browse,
      children: [
        { path: '', component: BrowseHome },
        { path: 'artist/:id', name: 'browse.artist', component: BrowseArtist, props: true },
        { path: 'album/:id', name: 'browse.album', component: BrowseAlbum, props: true },
        { path: 'track/:id', name: 'browse.track', component: BrowseTrack, props: true }
      ]
    }

  ]
})
