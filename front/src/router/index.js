import Vue from 'vue'
import Router from 'vue-router'
import PageNotFound from '@/components/PageNotFound'
import Home from '@/components/Home'
import Login from '@/components/auth/Login'
import Profile from '@/components/auth/Profile'
import Logout from '@/components/auth/Logout'
import Library from '@/components/library/Library'
import LibraryHome from '@/components/library/Home'
import LibraryArtist from '@/components/library/Artist'
import LibraryArtists from '@/components/library/Artists'
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
      component: Login,
      props: (route) => ({ next: route.query.next || '/library' })
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
      component: Favorites,
      props: (route) => ({
        defaultOrdering: route.query.ordering,
        defaultPage: route.query.page
      })
    },
    {
      path: '/library',
      component: Library,
      children: [
        { path: '', component: LibraryHome },
        {
          path: 'artists/',
          name: 'library.artists.browse',
          component: LibraryArtists,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        { path: 'artists/:id', name: 'library.artists.detail', component: LibraryArtist, props: true },
        { path: 'albums/:id', name: 'library.albums.detail', component: LibraryAlbum, props: true },
        { path: 'tracks/:id', name: 'library.tracks.detail', component: LibraryTrack, props: true },
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
    },
    { path: '*', component: PageNotFound }
  ]
})
