Rearranging Files
=================

Sometimes, rearranging the layout of documents in the docs folder can help to make
things a bit clearer for users. However, this can present the following issues:

- :ref:`Orphaned document links <orphaned-doc>`
- :ref:`Orphaned URLs <orphaned-url>`

.. _orphaned-doc:

Orphaned Document Links
-----------------------

Documents frequently reference other documents to avoid repeating information. If you
move a document, you need to be sure to update any orphaned references.

Running ``make html`` in the ``docs`` directory (assuming you have :doc:`Sphinx installed <tools>`)
will generate a series of warnings letting you know if any links are orphaned.

.. code-block:: shell
   
   funkwhale/docs/documentation/rearrange.rst:17: WARNING: unknown document: setup

You can then go to the file/line in question and update the link to its new location.

.. _orphaned-url:

Orphaned URLs
-------------

Once internal document links have been resolved, it is important to consider that the
moved file may have also been linked externally elsewhere before. In order to ensure
that anybody trying to access the file is properly redirected to its new location, we
need to make use of the link redirector in the ``conf.py`` file.

The link redirector takes two arguments: the old location of the file (passed as a .html
file at the relative path ``docs``), and the new location it should redirect to. For example,
if a document was moved from ``docs/index.html`` to ``docs/admin/index.html``, we would add
the following to the ``redirect_files`` section of ``conf.py``:

.. code-block:: python

   # -- Build legacy redirect files -------------------------------------------

   # Define list of redirect files to be build in the Sphinx build process

   redirect_files = [

      ('index.html', 'admin/index.html')
    ]

If you are moving something from one folder to another, you would need to tell the redirect
to move to the correct level. For example, if a file is moving from ``docs/admin/index.html``
to ``docs/users/index.html``, you will need to add the following to the ``redirect_files``
section of ``conf.py``:

.. code-block:: python

   # -- Build legacy redirect files -------------------------------------------

   # Define list of redirect files to be build in the Sphinx build process

   redirect_files = [

      ('admin/index.html', '../users/index.html') #The '..' tells the script to go up a level
    ]

The script will then take these two arguments and create a redirect file in the original
location so that anybody accessing the existing URL will be redirected.

