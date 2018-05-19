Simpler permission system (#152)


Simpler permission system
=========================

Starting from this release, the permission system is much simpler. Up until now,
we were using Django's built-in permission system, which was working, but also
quite complex to deal with.

The new implementation relies on simpler logic, which will make integration
on the front-end in upcoming releases faster and easier.

If you have manually given permissions to users on your instance,
you can migrate those to the new system.

On docker setups:

.. code-block:: shell

    docker-compose run --rm api python manage.py script django_permissions_to_user_permissions --no-input

On non-docker setups:

.. code-block:: shell

    # in your virtualenv
    python api/manage.py script django_permissions_to_user_permissions --no-input

There is still no dedicated interface to manage user permissions, but you
can use the admin interface at ``/api/admin/users/user/`` for that purpose in
the meantime.
