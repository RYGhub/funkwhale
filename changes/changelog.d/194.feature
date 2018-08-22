Authentication using a LDAP directory (#194)

Using a LDAP directory to authenticate to your Funkwhale instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funkwhale now support LDAP as an authentication source: you can configure
your instance to delegate login to a LDAP directory, which is especially
useful when you have an existing directory and don't want to manage users
manually.

You can use this authentication backend side by side with the classic one.

Have a look at https://docs.funkwhale.audio/installation/ldap.html
for detailed instructions on how to set this up.
