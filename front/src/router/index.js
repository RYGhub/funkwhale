import Vue from 'vue'
import Router from 'vue-router'
import PageNotFound from '@/components/PageNotFound'
import About from '@/components/About'
import Home from '@/components/Home'
import Authorize from '@/components/auth/Authorize'
import Login from '@/components/auth/Login'
import Signup from '@/components/auth/Signup'
import Profile from '@/components/auth/Profile'
import Settings from '@/components/auth/Settings'
import ApplicationNew from '@/components/auth/ApplicationNew'
import ApplicationEdit from '@/components/auth/ApplicationEdit'
import Logout from '@/components/auth/Logout'
import PasswordReset from '@/views/auth/PasswordReset'
import PasswordResetConfirm from '@/views/auth/PasswordResetConfirm'
import EmailConfirm from '@/views/auth/EmailConfirm'
import Library from '@/components/library/Library'
import LibraryHome from '@/components/library/Home'
import LibraryArtists from '@/components/library/Artists'
import LibraryArtistDetail from '@/components/library/ArtistDetail'
import LibraryArtistEdit from '@/components/library/ArtistEdit'
import LibraryArtistDetailBase from '@/components/library/ArtistBase'
import LibraryAlbums from '@/components/library/Albums'
import LibraryAlbumDetail from '@/components/library/AlbumDetail'
import LibraryAlbumEdit from '@/components/library/AlbumEdit'
import LibraryAlbumDetailBase from '@/components/library/AlbumBase'
import LibraryTrackDetail from '@/components/library/TrackDetail'
import LibraryTrackEdit from '@/components/library/TrackEdit'
import EditDetail from '@/components/library/EditDetail'
import LibraryTrackDetailBase from '@/components/library/TrackBase'
import LibraryRadios from '@/components/library/Radios'
import RadioBuilder from '@/components/library/radios/Builder'
import RadioDetail from '@/views/radios/Detail'
import PlaylistDetail from '@/views/playlists/Detail'
import PlaylistList from '@/views/playlists/List'
import Favorites from '@/components/favorites/List'
import AdminSettings from '@/views/admin/Settings'
import AdminLibraryBase from '@/views/admin/library/Base'
import AdminLibraryEditsList from '@/views/admin/library/EditsList'
import AdminLibraryArtistsList from '@/views/admin/library/ArtistsList'
import AdminLibraryArtistsDetail from '@/views/admin/library/ArtistDetail'
import AdminLibraryAlbumsList from '@/views/admin/library/AlbumsList'
import AdminLibraryAlbumDetail from '@/views/admin/library/AlbumDetail'
import AdminLibraryTracksList from '@/views/admin/library/TracksList'
import AdminLibraryTrackDetail from '@/views/admin/library/TrackDetail'
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
      path: '/authorize',
      name: 'authorize',
      component: Authorize,
      props: (route) => ({
        clientId: route.query.client_id,
        redirectUri: route.query.redirect_uri,
        scope: route.query.scope,
        responseType: route.query.response_type,
        nonce: route.query.nonce,
        state: route.query.state,
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
      path: '/settings/applications/new',
      name: 'settings.applications.new',
      component: ApplicationNew
    },
    {
      path: '/settings/applications/:id/edit',
      name: 'settings.applications.edit',
      component: ApplicationEdit,
      props: true
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
          path: 'edits',
          name: 'manage.library.edits',
          component: AdminLibraryEditsList,
          props: (route) => {
            return {
              defaultQuery: route.query.q,
            }
          }
        },
        {
          path: 'artists',
          name: 'manage.library.artists',
          component: AdminLibraryArtistsList,
          props: (route) => {
            return {
              defaultQuery: route.query.q,
            }
          }
        },
        {
          path: 'artists/:id',
          name: 'manage.library.artists.detail',
          component: AdminLibraryArtistsDetail,
          props: true
        },
        {
          path: 'albums',
          name: 'manage.library.albums',
          component: AdminLibraryAlbumsList,
          props: (route) => {
            return {
              defaultQuery: route.query.q,
            }
          }
        },
        {
          path: 'albums/:id',
          name: 'manage.library.albums.detail',
          component: AdminLibraryAlbumDetail,
          props: true
        },
        {
          path: 'tracks',
          name: 'manage.library.tracks',
          component: AdminLibraryTracksList,
          props: (route) => {
            return {
              defaultQuery: route.query.q,
            }
          }
        },
        {
          path: 'tracks/:id',
          name: 'manage.library.tracks.detail',
          component: AdminLibraryTrackDetail,
          props: true
        },
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
        {
          path: 'artists/:id',
          component: LibraryArtistDetailBase,
          props: true,
          children: [
            {
              path: '',
              name: 'library.artists.detail',
              component: LibraryArtistDetail
            },
            {
              path: 'edit',
              name: 'library.artists.edit',
              component: LibraryArtistEdit
            },
            {
              path: 'edit/:editId',
              name: 'library.artists.edit.detail',
              component: EditDetail,
              props: true,
            }
          ]
        },
        {
          path: 'albums/:id',
          component: LibraryAlbumDetailBase,
          props: true,
          children: [
            {
              path: '',
              name: 'library.albums.detail',
              component: LibraryAlbumDetail
            },
            {
              path: 'edit',
              name: 'library.albums.edit',
              component: LibraryAlbumEdit
            },
            {
              path: 'edit/:editId',
              name: 'library.albums.edit.detail',
              component: EditDetail,
              props: true,
            }
          ]
        },
        {
          path: 'tracks/:id',
          component: LibraryTrackDetailBase,
          props: true,
          children: [
            {
              path: '',
              name: 'library.tracks.detail',
              component: LibraryTrackDetail
            },
            {
              path: 'edit',
              name: 'library.tracks.edit',
              component: LibraryTrackEdit
            },
            {
              path: 'edit/:editId',
              name: 'library.tracks.edit.detail',
              component: EditDetail,
              props: true,
            }
          ]
        },
      ]
    },
    { path: '*', component: PageNotFound }
  ]
})
