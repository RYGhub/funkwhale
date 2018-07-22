Expose ActivityPub actors for users (#317)

Users now have an ActivityPub Actor [Manual action required]
------------------------------------------------------------

In the process of implementing federation for user activity such as listening
history, we are now making user profiles (a.k.a. ActivityPub actors) available through federation.

This does not means the federation is working, but this is a needed step to implement it.

Those profiles will be created automatically for new users, but you have to run a command
to create them for existing users.

On docker setups::

    docker-compose run --rm api python manage.py script create_actors --no-input

On non-docker setups::

    python manage.py script create_actors --no-input

This should only take a few seconds to run. It is safe to interrupt the process or rerun it multiple times.
