We now have a brand new instance settings interface in the front-end (#206)


Instance settings interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prior to this release, the only way to update instance settings (such as
instance description, signup policy, federation configuration, etc.) was using
the admin interface provided by Django (the back-end framework which power the API).

This interface worked, but was not really-user friendly and intuitive.

Starting from this release, we now offer a dedicated interface directly
in the front-end. You can view and edit all your instance settings from here,
assuming you have the required permissions.

This interface is available at ``/manage/settings` and via link in the sidebar.
