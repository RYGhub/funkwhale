Writing reStructuredText
========================

Funkwhale's documentation is written using a standard markup language called
`reStructuredText <http://docutils.sourceforge.net/rst.html>`_. It is similar to Markdown
and other web-based markup languages, but is better suited to technical documentation
due to its standardized nature. A full syntax breakdown can be found `here <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_,
but the following should be enough to get you started on writing docs for Funkwhale.

Headings
--------

Headings are useful for splitting up text into relevant subsections. With `Sphinx <http://www.sphinx-doc.org/>`_,
major headers and direct subheaders are rendered as navigation links on Index pages, which
makes them ideal for sharing specific information quickly. 

Headers are written like so:

.. code-block:: rst

   Header 1 //Equivalent to <h1>
   ========

   Header 2 //Equivalent to <h2>
   --------
   
   Header 3 //Equivalent to <h3>
   ^^^^^^^^

.. note::

   Underlines should be **at least** as long as the words they underline

Links
-----

Links can be rendered in several different ways depending on where they link to:

.. code-block:: rst

   `external link <https://example-url/>`_

   :doc:`link to document <../relative/doc/path>`

Inline references can also be generated using the following syntax:

.. code-block:: rst

   :ref:`This links to the text <link-ref>`

   .. _link-ref:

   The text you want to jump to

Lists
-----

Bullet point lists are usually written using dashes like so:

.. code-block:: rst

   - Item 1
   - Item 2
   - Item 3

Blocks
------

Blocks can be used to easily and concisely present information to a reader and are
particularly useful when demonstrating technical steps. Blocks in reStructuredText can
be written as follows:

.. code-block:: rst

   .. code-block:: shell

      write terminal commands here

   .. code-block:: python
      
      write Python code here

   .. code-block:: text

      write text here

Other syntax highlighting is available. See the spec for full details.

.. note::

   Content within code blocks should be indented by three spaces. You can end the code block by
   removing the indent.

Notes and Warnings
------------------

Notes are great for presenting important information to users and providing additional context.
Warnings can be very useful if a step you're writing about could potentially have adverse consequences.

.. code-block:: rst

   .. note::

      Your note goes here

   .. warning::

      Your warning goes here!

.. note::

   Content within notes and warnings should be indented by three spaces. You can end the block by
   removing the indent.

