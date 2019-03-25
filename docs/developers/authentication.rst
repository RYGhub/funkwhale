API Authentication
==================

Each Funkwhale API endpoint supports access from:

- Anonymous users (if the endpoint is configured to do so, for exemple via the ``API Authentication Required`` setting)
- Logged-in users
- Third-party apps (via OAuth2)

To seamlessly support this range of access modes, we internally use oauth scopes
to describes what permissions are required to perform any given operation.

OAuth
-----

Create an app
:::::::::::::

To connect to Funkwhale API via OAuth, you need to create an application. There are
two ways to do that:

1. By visiting ``/settings/applications/new`` when logged in on your Funkwhale instance.
2. By sending a ``POST`` request to ``/api/v1/oauth/apps/``, as described in `our API documentation <https://docs.funkwhale.audio/swagger/>`_.

Both method will give you a client ID and secret.

Getting an access token
:::::::::::::::::::::::

Once you have a client ID and secret, you can request access tokens
using the `authorization code grant flow <https://tools.ietf.org/html/rfc6749#section-4.1>`_.

We support the ``urn:ietf:wg:oauth:2.0:oob`` redirect URI for non-web applications, as well
as traditionnal redirection-based flow.

Our authorization endpoint is located at ``/authorize``, and our token endpoint at ``/api/v1/oauth/token/``.

Refreshing tokens
:::::::::::::::::

When your access token is expired, you can `request a new one as described in the OAuth specification <https://tools.ietf.org/html/rfc6749#section-6>`_.

Security considerations
:::::::::::::::::::::::

- Grant codes are valid for a 5 minutes after authorization request is approved by the end user.
- Access codes are valid for 10 hours. When expired, you will need to request a new one using your refresh token.
- We return a new refresh token everytime an access token is requested, and invalidate the old one. Ensure you store the new refresh token in your app.


Scopes
::::::

Scopes are defined in :file:`funkwhale_api/users/oauth/scopes.py:BASE_SCOPES`, and generally are mapped to a business-logic resources (follows, favorites, etc.). All those base scopes come in two flawours:

- `read:<base_scope>`: get read-only access to the resource
- `write:<base_scope>`: get write-only access to the ressource

For example, ``playlists`` is a base scope, and ``write:playlists`` is the actual scope needed to perform write
operations on playlists (via a ``POST``, ``PATCH``, ``PUT`` or ``DELETE``. ``read:playlists`` is used
to perform read operations on playlists such as fetching a given playlist via ``GET``.

Having the generic ``read`` or ``write`` scope give you the corresponding access on *all* resources.

This is the list of OAuth scopes that third-party applications can request:


+-------------------------------------------+---------------------------------------------------+
| Scope                                     | Description                                       |
+===========================================+===================================================+
| ``read``                                  | Read-only access to all data                      |
|                                           | (equivalent to all ``read:*`` scopes)             |
+-------------------------------------------+---------------------------------------------------+
| ``write``                                 | Write-only access to all data                     |
|                                           | (equivalent to all ``write:*`` scopes)            |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:profile``                  | Access to profile data (email, username, etc.)    |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:libraries``                | Access to library data (uploads, libraries        |
|                                           | tracks, albums, artists...)                       |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:favorites``                | Access to favorites                               |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:listenings``               | Access to history                                 |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:follows``                  | Access to followers                               |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:playlists``                | Access to playlists                               |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:radios``                   | Access to radios                                  |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:filters``                  | Access to content filters                         |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:notifications``            | Access to notifications                           |
+-------------------------------------------+---------------------------------------------------+
| ``<read/write>:edits``                    | Access to metadata edits                          |
+-------------------------------------------+---------------------------------------------------+
