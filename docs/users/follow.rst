Following Libraries
====================

Funkwhale's major strength is its focus on federated sharing of music. Users can share
music with one another through the network using library links.

Library Permissions
-------------------

Libraries are set up with specific permissions that determine their visibility to users on the local instance
and wider federated network. These permissions also determine whether or not follow requests need to be accepted
by the library owner. These permissions are as follows:

- **Everyone, across all instances** - the library will automatically accept follows from all users
- **Everyone on this instance** - the library will automatically accept follows from users on the same instance, but external users will need to be accepted by the library owner
- **Nobody Except Me** - all follows will need to be approved by the library owner

Getting Library Links
---------------------

The first step to following a library is getting a valid library link. These links typically look like
``https://instance-url/federation/music/libraries/a-random-string-of-numbers-and-letters``. Users can
share their library links with you directly, or you can find the library links for public libraries by
visiting their instance. To do this:

- Visit the instance containing the library you wish to follow
- Select an item contained within the library
- Scroll down to the "User libraries" section. You should see the name of the library in question
- The library link will be under "Sharing link". Click on "Copy" to copy the link to your clipboard

Following Other Libraries
--------------------------

Once you've got the library link, you can start following the library by doing the following:

- Click on the upload icon on the side bar
- Select "Get Started" under the "Follow Remote Libraries" section
- Paste the library link in the search bar and click on the magnifying glass
- Click on the "Follow" button when the library card appears

If another user on your instance has followed a library, you can follow it as well in case the user
leaves or stops following it. To do this:

- Select an item contained within the library on your instance
- Scroll down to the "User libraries" section. You should see the name of the library in question
- Click on "Follow"

Sharing Your Libraries
----------------------

As well as being able to follow other users, you can also share your libraries with friends, family, and
the network at large. To find your library link:

- Navigate to ``https://your-instance/content/libraries`` or click the upload button and select "Get Started"
  under the "Upload third-party content in a library" section to access your libraries
- Find the library in question and click on the "Details" button
- The sharing link should be shown on under the library details. Click on the "Copy" button to copy the link
- Share this link with other users