Message Rewrite Facility (MRF)
==============================

Funkwhale includes a feature that mimics `Pleroma's Message Rewrite Facility <https://docs-develop.pleroma.social/mrf.html>`_.
Using the MRF, instance admins can write and configure custom and automated moderation rules
that couldn't be implemented otherwise using :doc:`our other built-in moderation tools <../moderator/index>`.

Architecture
------------

The MRF is a pluggable system that will process messages and forward those to the list
of registered policies, in turn. Each policy can mutate the message, leave it as is, or discard it entirely.

Some of our built-in moderation tools are actually implemented as a MRF policy, e.g:

- Allow-list, when checking incoming messages (`code <https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/api/funkwhale_api/moderation/mrf_policies.py>`_)
- Domain and user blocking, when checking incoming messages (`code <https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/mrf_policies.py>`_)

.. note::

    While Pleroma MRF policies can also affect outgoing messages, this is not supported yet in Funkwhale.


Disclaimer
----------

Writing custom MRF can impact negatively the performance and stability of your pod, as well as message
delivery. Your policy will be called everytime a message is delivered, so ensure you don't execute
any slow operation here.

Please note that the Funkwhale developers consider custom MRF policy modules to fall under the purview of the AGPL. As such, you are obligated to release the sources to your custom MRF policy modules upon request.

Writing your first MRF policy
-----------------------------

MRF Policies are written as Python 3 functions that take at least one ``payload`` parameter.
This payload is the raw ActivityPub message, received via HTTP, after the HTTP signature check.

In the example below we write a policy that discards all Follow requests from listed domains:

.. code-block:: python

    import urllib.parse
    from funkwhale_api.moderation import mrf

    BLOCKED_FOLLOW_DOMAINS = ['domain1.com', 'botdomain.org']

    # registering the policy is required to have it applied
    # the name can be anything you want, it will appear in the mrf logs
    @mrf.inbox.register(name='blocked_follow_domains')
    def blocked_follow_domains_policy(payload, **kwargs):
        actor_id = payload.get('actor')
        domain = urllib.parse.urlparse(actor_id).hostname
        if domain not in BLOCKED_FOLLOW_DOMAINS:
            # raising mrf.Skip isn't strictly necessary but it provides
            # for info in the debug logs. Otherwise, you can simply return
            raise mrf.Skip("This domain isn't blocked")

        activity_type = payload.get('type')
        object_type = payload.get('object', {}).get('type')

        if object_type == 'Follow' and activity_type == 'Create':
            raise mrf.Discard('Follow from blocked domain')


This code must be stored in a Funkwhale plugin. To create one, just execute the following:

.. code-block:: shell

    # plugin name must contain only ASCII letters, numbers and undercores
    export PLUGIN_NAME="myplugin"
    # this is the default path where Funkwhale will look for plugins
    # if you want to use another path, update this path and ensure
    # your PLUGINS_PATH is also included in your .env
    export PLUGINS_PATH="/srv/funkwhale/plugins/"
    mkdir -p $PLUGINS_PATH/$PLUGIN_NAME
    cd $PLUGINS_PATH/$PLUGIN_NAME

    touch __init__.py  # required to make the plugin a valid Python package
    # create the required apps.py file to register our plugin in Funkwhale
    cat > apps.py <<EOF
    from django.apps import AppConfig

    class Plugin(AppConfig):
        name = "$PLUGIN_NAME"

    EOF

Once you have a Funkwhale plugin, simply put your MRF policy code inside a ``mrf_policies.py``
file whithin the plugin directory. Then enable the plugin in your ``.env`` by
adding its name to the coma-separated list of ``FUNKWHALE_PLUGINS`` (add the variable if it's not there).


Testing a MRF policy
--------------------

To make the job of writing and debugging MRF policies easier, we provide a management
command:

.. code-block:: shell

    python manage.py mrf_check --help
    # list registered MRF policies
    python manage.py mrf_check --list

    # check how our MRF would handle a legit follow
    export MRF_MESSAGE='{"actor": "https://normal.domain/@alice", "type": "Create", "object": {"type": "Follow"}}'
    echo $MRF_MESSAGE | python manage.py mrf_check inbox - -p blocked_follow_domains

    # check how our MRF would handle a problematic follow
    export MRF_MESSAGE='{"actor": "https://botdomain.org/@bob", "type": "Create", "object": {"type": "Follow"}}'
    echo $MRF_MESSAGE | python manage.py mrf_check inbox - -p blocked_follow_domains

    # check against an activity already present in the database
    # you can get the UUID of activities by visiting /api/admin/federation/activity
    export ACTIVITY_UUID="06208aea-c687-4e8b-aefd-22f1c3f76039"
    echo $MRF_MESSAGE | python manage.py mrf_check inbox $ACTIVITY_UUID -p blocked_follow_domains
