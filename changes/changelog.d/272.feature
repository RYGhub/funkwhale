Audio transcoding is back! (#272)


Audio transcoding is back!
--------------------------

After removal of our first, buggy transcoding implementation, we're proud to announce
that this feature is back. It is enabled by default, and can be configured/disabled
in your instance settings!

This feature works in the browser, with federated/non-federated tracks and using Subsonic clients.
Transcoded tracks are generated on the fly, and cached for a configurable amount of time,
to reduce the load on the server.
