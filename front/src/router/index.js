import Vue from "vue"
import Router from "vue-router"

Vue.use(Router)

console.log("PROCESS", process.env)
export default new Router({
  mode: "history",
  linkActiveClass: "active",
  base: process.env.VUE_APP_ROUTER_BASE_URL || "/",
  scrollBehavior(to, from, savedPosition) {
    return new Promise(resolve => {
      setTimeout(() => {
        if (to.hash) {
          resolve({ selector: to.hash });
        }
        let pos = savedPosition || { x: 0, y: 0 };
        resolve(pos);
      }, 100);
    });
  },
  routes: [
    {
      path: "/",
      name: "index",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/Home")
    },
    {
      path: "/front",
      name: "front",
      redirect: to => {
        const { hash, params, query } = to
        return { name: 'index', hash, query }
      }
    },
    {
      path: "/about",
      name: "about",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/About")
    },
    {
      path: "/login",
      name: "login",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/auth/Login"),
      props: route => ({ next: route.query.next || "/library" })
    },
    {
      path: "/notifications",
      name: "notifications",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/Notifications")
    },
    {
      path: "/auth/password/reset",
      name: "auth.password-reset",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/auth/PasswordReset"),
      props: route => ({
        defaultEmail: route.query.email
      })
    },
    {
      path: "/auth/email/confirm",
      name: "auth.email-confirm",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/auth/EmailConfirm"),
      props: route => ({
        defaultKey: route.query.key
      })
    },
    {
      path: "/auth/password/reset/confirm",
      name: "auth.password-reset-confirm",
      component: () =>
        import(
          /* webpackChunkName: "core" */ "@/views/auth/PasswordResetConfirm"
        ),
      props: route => ({
        defaultUid: route.query.uid,
        defaultToken: route.query.token
      })
    },
    {
      path: "/authorize",
      name: "authorize",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/auth/Authorize"),
      props: route => ({
        clientId: route.query.client_id,
        redirectUri: route.query.redirect_uri,
        scope: route.query.scope,
        responseType: route.query.response_type,
        nonce: route.query.nonce,
        state: route.query.state
      })
    },
    {
      path: "/signup",
      name: "signup",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/auth/Signup"),
      props: route => ({
        defaultInvitation: route.query.invitation
      })
    },
    {
      path: "/logout",
      name: "logout",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/auth/Logout")
    },
    {
      path: "/settings",
      name: "settings",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/auth/Settings")
    },
    {
      path: "/settings/applications/new",
      name: "settings.applications.new",
      props: route => ({
        scopes: route.query.scopes,
        name: route.query.name,
        redirect_uris: route.query.redirect_uris
      }),
      component: () =>
        import(
          /* webpackChunkName: "core" */ "@/components/auth/ApplicationNew"
        )
    },
    {
      path: "/settings/applications/:id/edit",
      name: "settings.applications.edit",
      component: () =>
        import(
          /* webpackChunkName: "core" */ "@/components/auth/ApplicationEdit"
        ),
      props: true
    },
    {
      path: "/@:username",
      name: "profile",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/auth/Profile"),
      props: true
    },
    {
      path: "/favorites",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/favorites/List"),
      props: route => ({
        defaultOrdering: route.query.ordering,
        defaultPage: route.query.page,
        defaultPaginateBy: route.query.paginateBy
      })
    },
    {
      path: "/content",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/content/Base"),
      children: [
        {
          path: "",
          name: "content.index",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/views/content/Home")
        }
      ]
    },
    {
      path: "/content/libraries/tracks",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/content/Base"),
      children: [
        {
          path: "",
          name: "content.libraries.files",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/views/content/libraries/Files"
            ),
          props: route => ({
            query: route.query.q
          })
        }
      ]
    },
    {
      path: "/content/libraries",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/content/Base"),
      children: [
        {
          path: "",
          name: "content.libraries.index",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/views/content/libraries/Home"
            )
        },
        {
          path: ":id/upload",
          name: "content.libraries.detail.upload",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/views/content/libraries/Upload"
            ),
          props: route => ({
            id: route.params.id,
            defaultImportReference: route.query.import
          })
        },
        {
          path: ":id",
          name: "content.libraries.detail",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/views/content/libraries/Detail"
            ),
          props: true
        }
      ]
    },
    {
      path: "/content/remote",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/views/content/Base"),
      children: [
        {
          path: "",
          name: "content.remote.index",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/views/content/remote/Home")
        }
      ]
    },
    {
      path: "/manage/settings",
      name: "manage.settings",
      component: () =>
        import(/* webpackChunkName: "admin" */ "@/views/admin/Settings")
    },
    {
      path: "/manage/library",
      component: () =>
        import(/* webpackChunkName: "admin" */ "@/views/admin/library/Base"),
      children: [
        {
          path: "edits",
          name: "manage.library.edits",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/EditsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "artists",
          name: "manage.library.artists",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/ArtistsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "artists/:id",
          name: "manage.library.artists.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/ArtistDetail"
            ),
          props: true
        },
        {
          path: "albums",
          name: "manage.library.albums",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/AlbumsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "albums/:id",
          name: "manage.library.albums.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/AlbumDetail"
            ),
          props: true
        },
        {
          path: "tracks",
          name: "manage.library.tracks",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/TracksList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "tracks/:id",
          name: "manage.library.tracks.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/TrackDetail"
            ),
          props: true
        },
        {
          path: "libraries",
          name: "manage.library.libraries",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/LibrariesList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "libraries/:id",
          name: "manage.library.libraries.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/LibraryDetail"
            ),
          props: true
        },
        {
          path: "uploads",
          name: "manage.library.uploads",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/UploadsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "uploads/:id",
          name: "manage.library.uploads.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/UploadDetail"
            ),
          props: true
        },
        {
          path: "tags",
          name: "manage.library.tags",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/TagsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "tags/:id",
          name: "manage.library.tags.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/library/TagDetail"
            ),
          props: true
        }
      ]
    },
    {
      path: "/manage/users",
      component: () =>
        import(/* webpackChunkName: "admin" */ "@/views/admin/users/Base"),
      children: [
        {
          path: "users",
          name: "manage.users.users.list",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/users/UsersList"
            )
        },
        {
          path: "invitations",
          name: "manage.users.invitations.list",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/users/InvitationsList"
            )
        }
      ]
    },
    {
      path: "/manage/moderation",
      component: () =>
        import(/* webpackChunkName: "admin" */ "@/views/admin/moderation/Base"),
      children: [
        {
          path: "domains",
          name: "manage.moderation.domains.list",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/DomainsList"
            )
        },
        {
          path: "domains/:id",
          name: "manage.moderation.domains.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/DomainsDetail"
            ),
          props: true
        },
        {
          path: "accounts",
          name: "manage.moderation.accounts.list",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/AccountsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q
            }
          }
        },
        {
          path: "accounts/:id",
          name: "manage.moderation.accounts.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/AccountsDetail"
            ),
          props: true
        },
        {
          path: "reports",
          name: "manage.moderation.reports.list",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/ReportsList"
            ),
          props: route => {
            return {
              defaultQuery: route.query.q,
              updateUrl: true
            }
          }
        },
        {
          path: "reports/:id",
          name: "manage.moderation.reports.detail",
          component: () =>
            import(
              /* webpackChunkName: "admin" */ "@/views/admin/moderation/ReportDetail"
            ),
          props: true
        },
      ]
    },
    {
      path: "/library",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/library/Library"),
      children: [
        {
          path: "",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/components/library/Home"),
          name: "library.index"
        },
        {
          path: "artists/",
          name: "library.artists.browse",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/Artists"
            ),
          props: route => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultTags: Array.isArray(route.query.tag || [])
              ? route.query.tag
              : [route.query.tag],
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: "albums/",
          name: "library.albums.browse",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/Albums"
            ),
          props: route => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultTags: Array.isArray(route.query.tag || [])
              ? route.query.tag
              : [route.query.tag],
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: "radios/",
          name: "library.radios.browse",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/Radios"
            ),
          props: route => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: "radios/build",
          name: "library.radios.build",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/radios/Builder"
            ),
          props: true
        },
        {
          path: "radios/build/:id",
          name: "library.radios.edit",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/radios/Builder"
            ),
          props: true
        },
        {
          path: "radios/:id",
          name: "library.radios.detail",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/views/radios/Detail"),
          props: true
        },
        {
          path: "playlists/",
          name: "library.playlists.browse",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/views/playlists/List"),
          props: route => ({
            defaultOrdering: route.query.ordering,
            defaultQuery: route.query.query,
            defaultPaginateBy: route.query.paginateBy,
            defaultPage: route.query.page
          })
        },
        {
          path: "playlists/:id",
          name: "library.playlists.detail",
          component: () =>
            import(/* webpackChunkName: "core" */ "@/views/playlists/Detail"),
          props: route => ({
            id: route.params.id,
            defaultEdit: route.query.mode === "edit"
          })
        },
        {
          path: "tags/:id",
          name: "library.tags.detail",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/TagDetail"
            ),
          props: true
        },
        {
          path: "artists/:id",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/ArtistBase"
            ),
          props: true,
          children: [
            {
              path: "",
              name: "library.artists.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/ArtistDetail"
                )
            },
            {
              path: "edit",
              name: "library.artists.edit",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/ArtistEdit"
                )
            },
            {
              path: "edit/:editId",
              name: "library.artists.edit.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/EditDetail"
                ),
              props: true
            }
          ]
        },
        {
          path: "albums/:id",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/AlbumBase"
            ),
          props: true,
          children: [
            {
              path: "",
              name: "library.albums.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/AlbumDetail"
                )
            },
            {
              path: "edit",
              name: "library.albums.edit",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/AlbumEdit"
                )
            },
            {
              path: "edit/:editId",
              name: "library.albums.edit.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/EditDetail"
                ),
              props: true
            }
          ]
        },
        {
          path: "tracks/:id",
          component: () =>
            import(
              /* webpackChunkName: "core" */ "@/components/library/TrackBase"
            ),
          props: true,
          children: [
            {
              path: "",
              name: "library.tracks.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/TrackDetail"
                )
            },
            {
              path: "edit",
              name: "library.tracks.edit",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/TrackEdit"
                )
            },
            {
              path: "edit/:editId",
              name: "library.tracks.edit.detail",
              component: () =>
                import(
                  /* webpackChunkName: "core" */ "@/components/library/EditDetail"
                ),
              props: true
            }
          ]
        }
      ]
    },
    {
      path: "*/index.html",
      redirect: "/"
    },
    {
      path: "*",
      component: () =>
        import(/* webpackChunkName: "core" */ "@/components/PageNotFound")
    }
  ]
})
