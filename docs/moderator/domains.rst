Moderating Domains
==================

Moderation rules can be used to control how your instance interacts with other domains.
They can be useful for keeping unwanted material and users out of your instance.

Managing Domains
----------------

Add a Domain
^^^^^^^^^^^^

Adding a domain allows you to create rules pre-emptively and proactively moderate content on your
instance. Domains with which users have already interacted will appear in the domains list.

To add a new domain:

- Navigate to the "Moderation" menu under "Administration"
- Select "Domains" along the top
- In the top right, enter the URL of the domain you want to federate with in the "Add a domain" box and click "Add"
- You will then be taken to an overview page showing details about the instance

Purge Domain Data
^^^^^^^^^^^^^^^^^

.. warning::

   Purging domain data will remove all tracks, libraries, and caches associated with
   the domain. This can have severe knock-on effects for users who have any of these
   in their favorites, playlists, or followed libraries. Be careful when performing
   this action.

Purging data from a domain can be useful if a domain is uploading offensive or illegal
media you do not want served on your instance.

- Navigate to the "Moderation" menu under "Administration"
- Select "Domains" along the top
- Find the domain whose data you wish to purge and select the checkbox next to it
- Select "Purge" from the "Actions" drop-down menu and click on "Go"
- A pop up will appear warning you of the consequences. If you want to continue with the purge, click "Launch"

Moderation Rules
----------------

Add a Moderation Rule to a Domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moderation rules can be useful for managing interaction with domains.

To add a moderation rule:

- Navigate to the "Moderation" menu under "Administration"
- Select "Domains" along the top
- Find the domain you wish to add a rule to and click on it
- In the top right, select "Add a moderation policy"
- Give a reason for your rule creation in the "Reason" box. This can help other moderators understand the action
- To block all interaction with the domain **and purge all content**, select "Block Everything"
- To only block media elements such as audio, avatars, and album art, select "Reject Media"
- When you have finished creating your rule, click "Create" to save the rule

Edit a Moderation Rule
^^^^^^^^^^^^^^^^^^^^^^

Sometimes a previously created moderation rule needs to be updated to lessen or increase
its severity.

To update an existing moderation rule:

- Navigate to the "Moderation" menu under "Administration"
- Select "Domains" along the top
- Find the domain whose rule you wish to edit and click on it
- In the top right, select "Update" under your existing rule
- Update the reason for your rule creation in the "Reason" box. This can help other moderators understand the action
- To block all interaction with the domain **and purge all content**, select "Block Everything"
- To only block media elements such as audio, avatars, and album art, select "Reject Media"
- When you have finished editing your rule, click "Create" to save the rule

Remove a Moderation Rule From a Domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a domain is no longer subject to moderation, you can remove existing rules to enable
full federation with the instance again.

To remove a moderation rule from a domain:

- Navigate to the "Moderation" menu under "Administration"
- Select "Domains" along the top
- Find the domain you wish to remove a rule from and click on it
- In the top right, select "Update" under your existing rule
- Click on "Delete"
- A pop up will appear warning that the action is irreversible. If you want to continue, select "Delete moderation rule"
