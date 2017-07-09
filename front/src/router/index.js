import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/auth/Login'
import Profile from '@/components/auth/Profile'
import Logout from '@/components/auth/Logout'
import Library from '@/components/library/Library'
import LibraryHome from '@/components/library/Home'
import LibraryArtist from '@/components/library/Artist'
import LibraryAlbum from '@/components/library/Album'
import LibraryTrack from '@/components/library/Track'
import LibraryImport from '@/components/library/import/Main'
import BatchList from '@/components/library/import/BatchList'
import BatchDetail from '@/components/library/import/BatchDetail'

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
      path: '/library',
      component: Library,
      children: [
        { path: '', component: LibraryHome },
        { path: 'artist/:id', name: 'library.artist', component: LibraryArtist, props: true },
        { path: 'album/:id', name: 'library.album', component: LibraryAlbum, props: true },
        { path: 'track/:id', name: 'library.track', component: LibraryTrack, props: true },
        {
          path: 'import/launch',
          name: 'library.import.launch',
          component: LibraryImport,
          props: (route) => ({ mbType: route.query.type, mbId: route.query.id })
        },
        {
          path: 'import/batches',
          name: 'library.import.batches',
          component: BatchList,
          children: [
          ]
        },
        { path: 'import/batches/:id', name: 'library.import.batches.detail', component: BatchDetail, props: true }
      ]
    }

  ]
})
