Moderating Users
==================

Moderation rules can be used to control how your instance interacts with accounts on other domains.
They can be useful for keeping unwanted material and users out of your instance.

Managing Accounts
-----------------

Purge Account Data
^^^^^^^^^^^^^^^^^^

.. warning::

   Purging account data will remove all tracks, libraries, and caches associated with
   the account. This can have severe knock-on effects for users who have any of these
   in their favorites, playlists, or followed libraries. Be careful when performing
   this action.

Purging data from an account can be useful if the account is uploading offensive or illegal
media you do not want served on your instance.

- Navigate to the "Moderation" menu under "Administration"
- Select "Accounts" along the top
- Find the account whose data you wish to purge and select the checkbox next to it
- Select "Purge" from the "Actions" drop-down menu and click on "Go"
- A pop up will appear warning you of the consequences. If you want to continue with the purge, click "Launch"

Moderation Rules
----------------

Add a Moderation Rule to an Account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   Moderation rules only apply to accounts on other instances

Moderation rules can be useful for managing interaction with Accounts.

To add a moderation rule:

- Navigate to the "Moderation" menu under "Administration"
- Select "Accounts" along the top
- Find the Account you wish to add a rule to and click on it
- In the top right, select "Add a moderation policy"
- Give a reason for your rule creation in the "Reason" box. This can help other moderators understand the action
- To block all interaction with the account **and purge all content**, select "Block Everything"
- To only block media elements such as audio, avatars, and album art, select "Reject Media"
- When you have finished creating your rule, click "Create" to save the rule

Edit a Moderation Rule
^^^^^^^^^^^^^^^^^^^^^^

Sometimes a previously created moderation rule needs to be updated to lessen or increase
its severity.

To update an existing moderation rule:

- Navigate to the "Moderation" menu under "Administration"
- Select "Accounts" along the top
- Find the account whose rule you wish to edit
- In the top right, select "Update" under your existing rule
- Update the reason for your rule creation in the "Reason" box. This can help other moderators understand the action
- To block all interaction with the account **and purge all content**, select "Block Everything"
- To only block media elements such as audio, avatars, and album art, select "Reject Media"
- When you have finished editing your rule, click "Create" to save the rule

Remove a Moderation Rule From an Account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If an account is no longer subject to moderation, you can remove existing rules to enable
full federation with the instance again.

To remove a moderation rule from an Account:

- Navigate to the "Moderation" menu under "Administration"
- Select "Accounts" along the top
- Find the account you wish to remove a rule from and click on it
- In the top right, select "Update" under your existing rule
- Click on "Delete"
- A pop up will appear warning that the action is irreversible. If you want to continue, select "Delete moderation rule"
