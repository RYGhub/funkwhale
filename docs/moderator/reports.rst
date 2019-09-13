Handling user reports
=====================

:doc:`Users can submit reports </users/reports>` in various places. When they do so,
their report ends up in a moderation queue until it is reviewed and resolved by a moderator.

View unresolved reports
-----------------------

Assuming you have the moderation permission, you'll find a "Moderation" link in the sidebar.

Clicking on this link will bring you to the list of unresolved reports. For convenience,
the number of unresolved reports (if any) is also displayed directly next to this link, and updated in real time
when new reports are submitted.

Email notifications
-------------------

In addition to the web UI, all moderators will receive a notification email whenever a report is 
submitted or resolved providing your pod has a valid email sending configuration. 
This notification will include a link to review and handle the report, as well as additional 
information about the report itself.

Handling reports
----------------

When viewing the moderation queue, you will be presented with the list of unresolved reports.

Each report in the queue should include all the information you need to handle it, in particular:

- Who submitted the report (or the email adress of the submitter if it's an accountless report)
- The report content
- A link to the reported object, and a copy of this object data at the time the report was submitted

When you mark a report as resolved, the report will simply be removed from the queue, and you can proceed to the next one.

Doing so will also assign the report to you, so other moderators can see who handled a given report.

Internal Notes
--------------

Whenever you need to perform an action because of a report, you can use the included form to leave a note to other moderators, or even yourself, for reference.

These notes are viewable by instance admins and moderators only.
