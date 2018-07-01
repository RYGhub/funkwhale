Federation
==========

Each Funkwale instance can federates its music library with other instances
of the network. This means that an instance A can acquire music from instance B
and share its own library with an instance C.

We support various levels of controls for federation-related features.

Managing federation
-------------------

Federation management is only available to instance admins and users
who have the proper permissions. You can disable federation completely
at the instance level by editing the ``federation__enabled`` :ref:`setting <instance-settings>`.

On the front end, assuming you have the proper permission, you will see
a "Federation" link in the sidebar.


Acquire music via federation
----------------------------

Instance libraries are protected by default. To access another instance
library, you have to follow it. Each Funkwhale instance gets a dedicated
ActivityPub Actor you can follow via the username "library@yourinstance.domain".

When submitted, a follow request will be sent to
the other instance which can accept or deny it. Once your follow request
is accepted, you can start browsing the other instance library
and import music from it.

By default, we do not duplicate audio files from federated tracks, to reduce
disk usage on your instance. When someone listens to a federated track,
the audio file is requested on the fly from the remote instance, and
store in a local cache. It is automatically deleted after a configurable
amount of time if it was not listened again in the meantime.

If you want to mirror a remote instance collection, including its audio files,
we offer an option for that.

We also support an "autoimport" mode for each remote library. When enabled,
any new track published in the remote library will be directly imported
in your instance.

Share music via federation
--------------------------

Federation is enabled by default, but requires manually approving
each other instance asking for access to library. This is by design,
to ensure your library is not shared publicly without your consent.

However, if you're confident about federating publicly without manual approval,
you can set the ``federation__music_needs_approval`` :ref:`setting <instance-settings>` to false.
Follow requests will be accepted automatically and followers
given access to your library without manual intervention.
