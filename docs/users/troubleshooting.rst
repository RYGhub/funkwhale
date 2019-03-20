End-User Troubleshooting
========================

Various errors and issues can arise on your Funkwhale instance, caused by configuration errors,
deployment/environment specific issues, or bugs in the software itself.

On this document, you'll find:

- Tools and commands you can use to better understand the issues
- A list of common pitfalls and errors and how to solve them
- A collection of links and advice to get help from the community and report new issues

Diagnose problems
^^^^^^^^^^^^^^^^^

Funkwhale is made of several components, each one being a potential cause for failure. Having an even basic overview
of Funkwhale's technical architecture can help you understand what is going on. You can refer to :doc:`the technical architecture <../developers/architecture>` for that.

Problems usually fall into one of those categories:

- **Frontend**: Funkwhale's interface is not loading, not behaving as expected, music is not playing
- **API**: the interface do not display any data or show errors
- **Import**: uploaded/imported tracks are not imported correctly or at all
- **Federation**: you cannot contact other Funkwhale servers, access their library, play federated tracks
- **Everything else**

Each category comes with its own set of diagnose tools and/or commands we will detail below. We'll also give you simple
steps for each type of problem. Please try those to see if it fix your issues. If none of those works, please report your issue on our
issue tracker.

Frontend issues
^^^^^^^^^^^^^^^

Diagnostic tools:

- Javascript and network logs from your browser console (see instructions on how to open it in `Chrome <https://developers.google.com/web/tools/chrome-devtools/console/>`_ and  `Firefox <https://developer.mozilla.org/en-US/docs/Tools/Web_Console/Opening_the_Web_Console>`_
- Proxy and API access and error logs
- The same operation works from a different browser

Common problems
***************

The front-end is completely blank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are visiting Funkwhale, but you don't see anything.

- Try from a different browser
- Check network errors in your browser console. If you see responses with 40X or 50X statuses, there is probably an issue with the webserver configuration
- If you don't see anything wrong in the network console, check the Javascript console
- Disable your browser extensions (like adblockers)

Music is not playing
~~~~~~~~~~~~~~~~~~~~

You have some tracks in your queue that don't play, or the queue is jumping from one track to the next until
there is no more track available:

- Try with other tracks. If it works with some tracks but not other tracks, this may means that the failing tracks are not probably imported
  or that your browser does not support a specific audio format
- Check the network and javascript console for potential errors

Tracks are not appending to the queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When clicking on "Play", "Play all albums" or "Play all" buttons, some tracks are not appended to the queue. This is
actually a feature of Funkwhale: those tracks have no file associated with them, so we cannot play them.

Specific pages are loading forever or blank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When viewing a given page, the page load never ends (you continue to see the spinner), or nothing seems to appear at all:

- Ensure your internet connection is up and running
- Ensure your instance is up and running
- Check the network and javascript console for potential errors

Report an issue or get help
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well be more than happy to help you to debug installation and configuration issues. The main channel
for receiving support about your Funkwhale installation is the `#funkwhale-troubleshooting:matrix.org <https://riot.im/app/#/room/#funkwhale-troubleshooting:matrix.org>`_ Matrix channel.

Before asking for help, we'd really appreciate if you took the time to go through this document and try to diagnose the problem yourself. But if you don't find
anything relevant or don't have the time, we'll be there for you!

Here are a few recommendations on how to structure and what to include in your help requests:

- Give us as much context as possible about your installation (OS, version, Docker/non-docker, reverse-proxy type, relevant logs and errors, etc.)
- Including screenshots or small gifs or videos can help us considerably when debugging front-end issues

You can also open issues on our `issue tracker <https://dev.funkwhale.audio/funkwhale/funkwhale/issues>`_. Please have a quick look for
similar issues before doing that, and use the issue tracker only to report bugs, suggest enhancements (both in the software and the documentation) or new features.

.. warning::

    If you ever need to share screenshots or urls with someone else, ensure those do not include your personal token.
    This token is binded to your account and can be used to connect and use your account.

    Urls that includes your token looks like: ``https://your.instance/api/v1/uploads/42/serve/?jwt=yoursecrettoken``

Improving this documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you feel like something should be improved in this document (and in the documentation in general), feel free to :doc:`contribute to the documentation <../documentation/creating>`.
If you're not comfortable contributing or would like to ask somebody else to do it, feel free to :doc:`request a change in documentation <../documentation/identifying>`.

