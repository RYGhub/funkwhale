import Vue from 'vue'
import Router from 'vue-router'
import PageNotFound from '@/components/PageNotFound'
import About from '@/components/About'
import Home from '@/components/Home'
import InstanceTimeline from '@/views/instance/Timeline'
import Login from '@/components/auth/Login'
import Signup from '@/components/auth/Signup'
import Profile from '@/components/auth/Profile'
import Settings from '@/components/auth/Settings'
import Logout from '@/components/auth/Logout'
import PasswordReset from '@/views/auth/PasswordReset'
import PasswordResetConfirm from '@/views/auth/PasswordResetConfirm'
import EmailConfirm from '@/views/auth/EmailConfirm'
import Library from '@/components/library/Library'
import LibraryHome from '@/components/library/Home'
import LibraryArtist from '@/components/library/Artist'
import LibraryArtists from '@/components/library/Artists'
import LibraryAlbum from '@/components/library/Album'
import LibraryTrack from '@/components/library/Track'
import LibraryImport from '@/components/library/import/Main'
import LibraryRadios from '@/components/library/Radios'
import RadioBuilder from '@/components/library/radios/Builder'
import RadioDetail from '@/views/radios/Detail'
import BatchList from '@/components/library/import/BatchList'
import BatchDetail from '@/components/library/import/BatchDetail'
import RequestsList from '@/components/requests/RequestsList'
import PlaylistDetail from '@/views/playlists/Detail'
import PlaylistList from '@/views/playlists/List'
import Favorites from '@/components/favorites/List'
import AdminSettings from '@/views/admin/Settings'
import AdminLibraryBase from '@/views/admin/library/Base'
import AdminLibraryFilesList from '@/views/admin/library/FilesList'
import FederationBase from '@/views/federation/Base'
import FederationScan from '@/views/federation/Scan'
import FederationLibraryDetail from '@/views/federation/LibraryDetail'
import FederationLibraryList from '@/views/federation/LibraryList'
import FederationTrackList from '@/views/federation/LibraryTrackList'
import FederationFollowersList from '@/views/federation/LibraryFollowersList'

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
      path: '/about',
      name: 'about',
      component: About
    },
    {
      path: '/activity',
      name: 'activity',
      component: InstanceTimeline
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      props: (route) => ({ next: route.query.next || '/library' })
    },
    {
      path: '/auth/password/reset',
      name: 'auth.password-reset',
      component: PasswordReset,
      props: (route) => ({
        defaultEmail: route.query.email
      })
    },
    {
      path: '/auth/email/confirm',
      name: 'auth.email-confirm',
      component: EmailConfirm,
      props: (route) => ({
        defaultKey: route.query.key
      })
    },
    {
      path: '/auth/password/reset/confirm',
      name: 'auth.password-reset-confirm',
      component: PasswordResetConfirm,
      props: (route) => ({
        defaultUid: route.query.uid,
        defaultToken: route.query.token
      })
    },
    {
      path: '/signup',
      name: 'signup',
      component: Signup
    },
    {
      path: '/logout',
      name: 'logout',
      component: Logout
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
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
        defaultPage: route.query.page,
        defaultPaginateBy: route.query.paginateBy
      })
    },
    {
      path: '/manage/settings',
      name: 'manage.settings',
      component: AdminSettings
    },
    {
      path: '/manage/federation',
      component: FederationBase,
      children: [
        {
          path: 'scan',
          name: 'federation.libraries.scan',
          component: FederationScan },
        {
          path: 'libraries',
          name: 'federation.libraries.list',
          component: FederationLibraryList,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: 'tracks',
          name: 'federation.tracks.list',
          component: FederationTrackList,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: 'followers',
          name: 'federation.followers.list',
          component: FederationFollowersList,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        { path: 'libraries/:id', name: 'federation.libraries.detail', component: FederationLibraryDetail, props: true }
      ]
    },
    {
      path: '/manage/library',
      component: AdminLibraryBase,
      children: [
        {
          path: 'files',
          name: 'manage.library.files',
          component: AdminLibraryFilesList
        }
      ]
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
        {
          path: 'radios/',
          name: 'library.radios.browse',
          component: LibraryRadios,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        { path: 'radios/build', name: 'library.radios.build', component: RadioBuilder, props: true },
        { path: 'radios/build/:id', name: 'library.radios.edit', component: RadioBuilder, props: true },
        { path: 'radios/:id', name: 'library.radios.detail', component: RadioDetail, props: true },
        {
          path: 'playlists/',
          name: 'library.playlists.browse',
          component: PlaylistList,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: 'playlists/:id',
          name: 'library.playlists.detail',
          component: PlaylistDetail,
          props: (route) => ({
            id: route.params.id,
            defaultEdit: route.query.mode === 'edit' })
        },
        { path: 'artists/:id', name: 'library.artists.detail', component: LibraryArtist, props: true },
        { path: 'albums/:id', name: 'library.albums.detail', component: LibraryAlbum, props: true },
        { path: 'tracks/:id', name: 'library.tracks.detail', component: LibraryTrack, props: true },
        {
          path: 'import/launch',
          name: 'library.import.launch',
          component: LibraryImport,
          props: (route) => ({
            source: route.query.source,
            request: route.query.request,
            mbType: route.query.type,
            mbId: route.query.id })
        },
        {
          path: 'import/batches',
          name: 'library.import.batches',
          component: BatchList,
          children: [
          ]
        },
        { path: 'import/batches/:id', name: 'library.import.batches.detail', component: BatchDetail, props: true },
        {
          path: 'requests/',
          name: 'library.requests',
          component: RequestsList,
          props: (route) => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page,
            defaultStatus: route.query.status || 'any'
          }),
          children: [
          ]
        }
      ]
    },
    { path: '*', component: PageNotFound }
  ]
})
