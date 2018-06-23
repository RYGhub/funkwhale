Funkwhale's front-end can now point to any instance (#327)

Removed front-end and back-end coupling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Eventhough Funkwhale's front-end has always been a Single Page Application,
talking to an API, it was only able to talk to an API on the same domain.

There was no real technical justification behind this (only lazyness), and it was
also blocking interesting use cases:

- Use multiple customized versions of the front-end with the same instance
- Use a customized version of the front-end with multiple instances
- Use a locally hosted front-end with a remote API, which is especially useful in development

From now on, Funkwhale's front-end can connect to any Funkwhale server. You can
change the server you are connecting to in the footer.

Fixing this also unlocked a really interesting feature in our development/review workflow:
by leveraging Gitlab CI and review apps, we are now able to deploy automatically live versions of
a merge request, making it possible for anyone to review front-end changes easily, without
the need to install a local environment.
