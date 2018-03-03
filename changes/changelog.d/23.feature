Basic activity stream for listening and favorites (#23)

A new "Activity" page is now available from the sidebar, where you can
browse your instance activity. At the moment, this includes other users
favorites and listening, but more activity types will be implemented in the
future.

Internally, we implemented those events by following the Activity Stream
specification, which will help us to be compatible with other networks
in the long-term.

A new settings page has been added to control the visibility of your activity.
By default, your activity will be browsable by anyone on your instance,
but you can switch to a full private mode where nothing is shared.

The setting form is available in your profile.
