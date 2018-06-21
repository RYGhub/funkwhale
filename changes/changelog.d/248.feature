New invite system (#248)


New invite system
^^^^^^^^^^^^^^^^^

On closed instances, it has always been a little bit painful to create accounts
by hand for new users. This release solve that by adding invitations.

You can generate invitation codes via the "users" admin interface (you'll find a
link in the sidebar). Those codes are valid for 14 days, and can be used once
to create a new account on the instance, even if registrations are closed.

By default, we generate a random code for invitations, but you can also use custom codes
if you need to print them or make them fancier ;)

Invitations generation and management requires the "settings" permission.
