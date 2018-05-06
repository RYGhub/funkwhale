Users can now request password reset by email, assuming
a SMTP server was correctly configured (#187)

Update
^^^^^^

Starting from this release, Funkwhale will send two types
of emails:

- Email confirmation emails, to ensure a user's email is valid
- Password reset emails, enabling user to reset their password without an admin's intervention

Email sending is disabled by default, as it requires additional configuration.
In this mode, emails are simply outputed on stdout.

If you want to actually send those emails to your users, you should edit your
.env file and tweak the EMAIL_CONFIG variable. See :ref:`setting-EMAIL_CONFIG`
for more details.

.. note::

  As a result of these changes, the DJANGO_EMAIL_BACKEND variable,
  which was not documented, has no effect anymore. You can safely remove it from
  your .env file if it is set.
