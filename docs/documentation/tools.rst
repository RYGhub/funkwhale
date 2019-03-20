Documentation Requirements
==========================

Funkwhale's documentation is written using :doc:`reStructuredText <restructured>` and is built using
`Sphinx <http://www.sphinx-doc.org/>`_.

Text Editor
-----------

As reStructuredText is a writing standard, any text editor can be used to modify documents depending on preference.
User-friendly programs such as `Retext <https://github.com/retext-project/retext>`_ are good options for
those just getting started with writing reStructuredText. Many other editors such as `Vim <https://www.vim.org/>`_, 
`Emacs <https://www.gnu.org/software/emacs/>`_, `VS Code <https://code.visualstudio.com/>`_, and
`Atom <https://atom.io/>`_ have addons which can help with syntax highlighting and live previewing.

Sphinx
------

Sphinx is used to generate a static site based on the ``.rst`` files in the ``docs`` directory. When writing
documents, it can be useful to build the site to see how your changes will look in production. To do this:

- Install Sphinx using `pip <https://pypi.org/project/pip/>`_

.. code-block:: shell

   pip install sphinx

- Navigate to your local ``funkwhale/docs`` directory

.. code-block:: shell

   cd funkwhale/docs

- Use the make file to build the site

.. code-block:: shell

   make html

- Sphinx will generate the site in your ``funkwhale/docs/_build`` directory unless otherwise stated

Once you have generated a local copy of the site, you can open it up by opening the index.html file in
``funkwhale/docs/_build``.

.. note::

    If you are familiar with `Docker <https://www.docker.com/>`_ and `docker-compose <https://docs.docker.com/compose/>`_, 
    you can also hack on the documentation via a single command: ``docker-compose -f dev.yml up docs``.

    This will make the documentation available at http://0.0.0.0:8001, with live-reloading enabled, so any change made in the 
    ``.rst`` files will be reflected immediately in your browser.


Git
---

In order to work on files on your computer, you will need to install `git <https://git-scm.com/>`_ for your
operating system. Git is used to push and pull files to and from the Funkwhale repository and track changes
made to documents/code alike.

Gitlab
------

If you are only making minor changes to a document or don't wish to install anything, you can use 
`Gitlab's <https://dev.funkwhale.audio>`_ built-in IDE. Once you have made an account and :doc:`created
a pull request <creating>`, you can click on the "Open in Web IDE" button to open up a fully-fledged
editor in your web browser.

