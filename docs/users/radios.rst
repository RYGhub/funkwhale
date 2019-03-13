
Using Radios
============

.. note::

   Currently, Funkwhale does not implement tags for use in radios. There is a lot of active disucssion
   around how to implement them, but in the meantime it is only possible to create artist radios.

Radios are a great way to discover new music, or even just create a dynamic playlist of songs you like.
By default, all users have access to three build-in radios:

- Favorites - this plays through your :doc:`favorite tracks <favorites>`
- Random - plays random songs from your :doc:`libraries <upload>` or :doc:`libraries you follow <follow>`
- Less Listened - plays songs you listen to less frequently

Creating a New Radio
--------------------

.. note::

   Any music that is in a private collection will appear in public radios but will not be playable unless the user has access to
   the containing library

In addition to the built-in radios, Funkwhale offers users the ability to create their own specific radios.
These radios can be shared with other users on your instance or kept entirely to yourself.

To create a new radio:

- Navigate to ``https://your-instance/library/radios`` or click "Browse Library" and select "Radios" along the top of the screen
- Under "User Radios", click "Create your own radio"
- Give your radio a name and description
- If you want to share your radio on your instance, check the "Display publicly" box. Otherwise, uncheck this to keep the radio private
- To set up the filters for your radio, click on "Select a filter" and select "Artist" from the drop-down menu. Click "Add Filter" to activate the filter
- To exclude certain artists, toggle the "Exclude" switch so it turns blue and then select the artists from the "Select artists" drop-down menu
- To only include certain artists, toggle the "Exclude" switch so it turns gray and then select the artists from the "Select artists" drop-down menu
- Click "Save" to save your radio

Listening to a Radio
--------------------

To start listening to a radio:

- Navigate to ``https://your-instance/library/radios`` or click "Browse Library" and select "Radios" along the top of the screen
- Find the radio you want to listen to and click on "Start radio"
- Your queue will be populated with the **currently playing** song and the **next song on the radio**

To stop listening to a radio:

- Open your :doc:`queue`
- Select "Stop Radio" at the bottom of the queue
- The songs that were queued will stay in your queue, but the radio will stop queueing new songs