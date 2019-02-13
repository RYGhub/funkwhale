import Vue from 'vue'
import Router from 'vue-router'
import PageNotFound from '@/components/PageNotFound'
import About from '@/components/About'
import Home from '@/components/Home'
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
import LibraryAlbums from '@/components/library/Albums'
import LibraryAlbum from '@/components/library/Album'
import LibraryTrack from '@/components/library/Track'
import LibraryRadios from '@/components/library/Radios'
import RadioBuilder from '@/components/library/radios/Builder'
import RadioDetail from '@/views/radios/Detail'
import PlaylistDetail from '@/views/playlists/Detail'
import PlaylistList from '@/views/playlists/List'
import Favorites from '@/components/favorites/List'
import AdminSettings from '@/views/admin/Settings'
import AdminLibraryBase from '@/views/admin/library/Base'
import AdminLibraryFilesList from '@/views/admin/library/FilesList'
import AdminUsersBase from '@/views/admin/users/Base'
import AdminUsersList from '@/views/admin/users/UsersList'
import AdminInvitationsList from '@/views/admin/users/InvitationsList'
import AdminModerationBase from '@/views/admin/moderation/Base'
import AdminDomainsList from '@/views/admin/moderation/DomainsList'
import AdminDomainsDetail from '@/views/admin/moderation/DomainsDetail'
import AdminAccountsList from '@/views/admin/moderation/AccountsList'
import AdminAccountsDetail from '@/views/admin/moderation/AccountsDetail'
import ContentBase from '@/views/content/Base'
import ContentHome from '@/views/content/Home'
import LibrariesHome from '@/views/content/libraries/Home'
import LibrariesUpload from '@/views/content/libraries/Upload'
import LibrariesDetail from '@/views/content/libraries/Detail'
import LibrariesFiles from '@/views/content/libraries/Files'
import RemoteLibrariesHome from '@/views/content/remote/Home'
import Notifications from '@/views/Notifications'

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
      path: '/front',
      name: 'front',
      redirect: '/'
    },
    {
      path: '/about',
      name: 'about',
      component: About
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      props: (route) => ({ next: route.query.next || '/library' })
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: Notifications
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
      component: Signup,
      props: (route) => ({
        defaultInvitation: route.query.invitation
      })
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
      path: '/content',
      component: ContentBase,
      children: [
        {
          path: '',
          name: 'content.index',
          component: ContentHome
        }
      ]
    },
    {
      path: '/content/libraries/tracks',
      component: ContentBase,
      children: [
        {
          path: '',
          name: 'content.libraries.files',
          component: LibrariesFiles,
          props: (route) => ({
            query: route.query.q
          })
        }
      ]
    },
    {
      path: '/content/libraries',
      component: ContentBase,
      children: [
        {
          path: '',
          name: 'content.libraries.index',
          component: LibrariesHome
        },
        {
          path: ':id/upload',
          name: 'content.libraries.detail.upload',
          component: LibrariesUpload,
          props: (route) => ({
            id: route.params.id,
            defaultImportReference: route.query.import
          })
        },
        {
          path: ':id',
          name: 'content.libraries.detail',
          component: LibrariesDetail,
          props: true
        }
      ]
    },
    {
      path: '/content/remote',
      component: ContentBase,
      children: [
        {
          path: '',
          name: 'content.remote.index',
          component: RemoteLibrariesHome
        }
      ]
    },
    {
      path: '/manage/settings',
      name: 'manage.settings',
      component: AdminSettings
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
      path: '/manage/users',
      component: AdminUsersBase,
      children: [
        {
          path: 'users',
          name: 'manage.users.users.list',
          component: AdminUsersList
        },
        {
          path: 'invitations',
          name: 'manage.users.invitations.list',
          component: AdminInvitationsList
        }
      ]
    },
    {
      path: '/manage/moderation',
      component: AdminModerationBase,
      children: [
        {
          path: 'domains',
          name: 'manage.moderation.domains.list',
          component: AdminDomainsList
        },
        {
          path: 'domains/:id',
          name: 'manage.moderation.domains.detail',
          component: AdminDomainsDetail,
          props: true
        },
        {
          path: 'accounts',
          name: 'manage.moderation.accounts.list',
          component: AdminAccountsList,
          props: (route) => {
            return {
              defaultQuery: route.query.q,

            }
          }
        },
        {
          path: 'accounts/:id',
          name: 'manage.moderation.accounts.detail',
          component: AdminAccountsDetail,
          props: true
        }
      ]
    },
    {
      path: '/library',
      component: Library,
      children: [
        { path: '', component: LibraryHome, name: 'library.index' },
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
          path: 'albums/',
          name: 'library.albums.browse',
          component: LibraryAlbums,
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
      ]
    },
    { path: '*', component: PageNotFound }
  ]
})
