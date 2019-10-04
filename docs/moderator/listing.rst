Allow-Listing
=============

The Allow-Listing feature grants pod moderators
and administrators greater control over federation
by allowing you to create a pod-wide allow-list.

When allow-listing is enabled, your pod's users will only
be able to interact with pods included in the allow-list.
Any messages, activity, uploads, or modifications to
libraries and playlists will only be shared with pods
on the allow-list. Pods which are not included in the
allow-list will not have access to your pod's content
or messages and will not be able to send anything to
your pod.

Enabling Allow-Listing
----------------------

.. warning::

   If your pod is already federating proceed with caution.
   Enabling the Allow-Listing feature will initially block
   all activity from external domains as the list will be
   empty

To enable allow-listing:

- Navigate to the "Settings" menu
- Go to the "Moderation" section
- Toggle the "Enable allow-listing" radio button
- Click "Save" to commit the change

Once enabled, you can start adding domains to your
allow-list.

Adding/Removing Domains
-----------------------

Add a New Domain
^^^^^^^^^^^^^^^^

- Navigate to the "Moderation" menu. Any domains currently
  in the allow-list will be visible here with a green check
  mark next to their name. Other pods with which you have previously
  interacted will also be visible here
- Type the domain name of the pod you wish to allow into
  the "Add a Domain" input box in the top-right of the screen
- Tick the "Add to allow-list" tickbox
- Click "Add" to add the domain

Add a Known Domain
^^^^^^^^^^^^^^^^^^

- Navigate to the "Moderation" menu. Any domains currently
  in the allow-list will be visible here with a green check
  mark next to their name. Other pods with which you have previously
  interacted will also be visible here
- Click on the tickbox next to the domain(s) you wish to add to
  the allow-list
- Select "Add to allow-list" from the drop-down menu titled "Actions"
  and click "Go" to add the domain(s)

Remove a Domain
^^^^^^^^^^^^^^^

To remove a domain from the allow-list:

- Navigate to the "Moderation" menu. Any domains currently
  in the allow-list will be visible here with a green check
  mark next to their name. Other pods with which you have previously
  interacted will also be visible here
- Click on the tickbox next to the domain(s) you wish to remove
  from the allow-list
- Select "Remove from allow-list" from the drop-down menu titled
  "Actions" and click "Go" to remove the domain(s)

Purging Existing Content
------------------------

Moderators can add and remove domains at any time, and removing
a domain from the allow-list will effectively block all future
content from being received on your pod. Previously received
messages and content from pods not on the allow-list will remain
until you purge it from your pod. To do this:

- Navigate to the "Moderation" menu. Any domains currently
  in the allow-list will be visible here with a green check
  mark next to their name. Other pods with which you have
  previously interacted will also be visible here
- Click on the tickbox next to the domain(s) you wish to purge
  received messages from
- Select "Purge" from the drop-down menu titled "Actions"
  and click "Go" to purge the messages
