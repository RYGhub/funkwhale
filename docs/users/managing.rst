Managing Libraries
==================

Managing your music libraries is an important part of using Funkwhale. In addition to :doc:`uploading new music <upload>`, you may also want to :ref:`edit your library's details <edit_library>`, :ref:`delete a library <delete_library>`, or :ref:`remove content from a library <remove_content>`.

If you are looking to publish content on Funkwhale directly, you can use :doc:`channels <channels>` instead

.. _create_library:

Creating a Library
------------------

To upload content to a library, you will first need to create one. To do this:

- Navigate to ``https://your-instance/content/libraries`` or click on the upload icon and 
  click on "Get Started" under the "Upload third-party content in a library" section
- Click on the "Create a new library" option under the "My Libraries" header to bring up the creation screen
- Enter the name, description, and privacy level of the library. The privacy level can be one of the following:

  - Public: anyone can follow the library to automatically access its content (including users on other instances)
  - Local: other users from your instance can follow the library to automatically access its content
  - Private: nobody apart from you can access the library content

- Click "Create Library" to save your changes

.. _upload_library:

Uploading Content to a Library
------------------------------

.. note::

   Content you upload to a library will inherit the privacy level of the library itself. Content not
   distributed under a permissive library should only be placed in private libraries

Once you have :ref:`created a library <create_library>`, you can start adding files to it. Before you
upload files, it is a good idea to :doc:`tag them correctly <tagging>` to make sure they have the right
metadata associated with it.

To upload content:

- Navigate to ``https://your-instance/content/libraries`` or click on the upload icon in the sidebar and 
  click on "Get Started" under the "Upload third-party content in a library" section
- Click "Upload" under the library you wish to edit
- You will see a summary of the upload date and information. Click "Proceed" to continue
- Drag and drop the files you would like to upload or click on the upload section to open the file picker
  and open the files
- The "Processing" tab will show the status of the uploads including any errors or warnings

.. note::

   If you try to navigate away from the upload screen before everything has finished uploading, you will
   be asked to confirm the navigation

.. _edit_library:

Editing a Library
-----------------

To change details about a library:

- Navigate to ``https://your-instance/content/libraries`` or click on the upload icon in the sidebar and 
  click on "Get Started" under the "Upload third-party content in a library" section
- Click "Detail" under the library you wish to edit
- Select "Edit" from the menu that appears
- In the edit menu, you will be able to change the name, description, and visibility of your library
- Make the changes you wish to make, then select "Update library" to save the changes

.. _delete_library:

Deleting a Library
------------------

.. warning::

   Deleting a library will also delete any content within the library. Make sure that content is backed up before continuing.

To delete a library:

- Navigate to ``https://your-instance/content/libraries`` or click on the upload icon in the sidebar and 
  click on "Get Started" under the "Upload third-party content in a library" section
- Click "Detail" under the library you wish to edit
- Select "Edit" from the menu that appears
- Select "Delete" from the bottom of the menu. A pop up will appear warning of the consequences of deleting the library. If you want to continue, click "Delete library"

.. _remove_content:

Removing Content From a Library
-------------------------------

.. warning::

   Removing content from your library deletes the file from the server. Make sure you have a backup of any files you want to keep.

To delete content from a library:

- Navigate to ``https://your-instance/content/libraries`` or click on the upload icon in the sidebar and 
  click on "Get Started" under the "Upload third-party content in a library" section
- Click "Detail" under the library you wish to edit- Select "Tracks" from the menu that appears
- Select all tracks you wish to remove by selecting the checkboxes next to them
- In the "Actions" drop down menu, select "Delete" and click "Go". A pop up will appear warning of the consequences of deleting the library. If you want to continue, click "Launch"
