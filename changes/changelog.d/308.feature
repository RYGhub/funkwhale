Store licensing and copyright information from file metadata, if available (#308)

Licensing and copyright information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funkwhale is now able to parse copyright and license data from file and store
this information. Apart from displaying it on each track detail page,
no additional behaviour is currently implemented to use this new data, but this
will change in future releases.

License and copyright data is also broadcasted over federation.

License matching is done on the content of the ``License`` tag in the files,
with a fallback on the ``Copyright`` tag.

Funkwhale will successfully extract licensing data for the following licenses:

- Creative Commons 0 (Public Domain)
- Creative Commons 1.0 (All declinations)
- Creative Commons 2.0 (All declinations)
- Creative Commons 2.5 (All declinations and countries)
- Creative Commons 3.0 (All declinations and countries)
- Creative Commons 4.0 (All declinations)

Support for other licenses such as Art Libre or WTFPL will be added in future releases.
