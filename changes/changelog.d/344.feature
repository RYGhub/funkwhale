Implemented a basic but functionnal Github-like search on federated tracks list (#344)


Improved search on federated tracks list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Having a powerful but easy-to-use search is important but difficult to achieve, especially
if you do not want to have a real complex search interface.

Github does a pretty good job with that, using a structured but simple query system
(See https://help.github.com/articles/searching-issues-and-pull-requests/#search-only-issues-or-pull-requests).

This release implements a limited but working subset of this query system. You can use it only on the federated
tracks list (/manage/federation/tracks) at the moment, but depending on feedback it will be rolled-out on other pages as well.

This is the type of query you can run:

- ``hello world``: search for "hello" and "world" in all the available fields
- ``hello in:artist`` search for results where artist name is "hello"
- ``spring in:artist,album`` search for results where artist name or album title contain "spring"
- ``artist:hello`` search for results where artist name equals "hello"
- ``artist:"System of a Down" domain:instance.funkwhale`` search for results where artist name equals "System of a Down" and inside "instance.funkwhale" library
