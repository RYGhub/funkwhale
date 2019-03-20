Adding New Documents
====================

Writing Documents
-----------------

Before you start writing documents: 

- Make sure you have all the necessary information and :doc:`tools you need <tools>` to get started 
- Check the `current documents <https://docs.funkwhale.audio>`_ carefully to make sure you're not repeating something somebody has already said
- Familiarize yourself with :doc:`reStructuredText <restructured>` and :doc:`the recommended document style <style>`

Once you're ready to get started, you can start :ref:`working with Gitlab <work-with-gitlab>`

.. _work-with-gitlab:

Working With Gitlab
-------------------

Documents are managed in the Funkwhale `Gitlab <https://dev.funkwhale.audio>`_ repository along with the code.
In order to add new documents, you will need to follow this process:

- :ref:`Sign up to Gitlab <sign-up>`
- :ref:`Fork the project <fork-project>`
- :ref:`Clone the Repository <clone-repo>`
- :ref:`Add documents to your branch <add-docs>`
- :ref:`Create a Merge Request <merge-request>`

.. _sign-up:

Signing up to Gitlab
^^^^^^^^^^^^^^^^^^^^

Before you can contribute documents to Funkwhale, you will need to set up an account on the
project's `Gitlab <https://dev.funkwhale.audio>`_. To do this:

- Navigate to the https://dev.funkwhale.audio
- Click on "register" to bring up the registration form
- Fill in the relevant details, or alternatively sign up with Github if you already have an account
- [Optional]: You can then `set up an SSH key <https://docs.gitlab.com/ee/ssh/>`_ to enable easy management of your :ref:`repository <clone-repo>`

.. _fork-project:

Fork the project
^^^^^^^^^^^^^^^^

Once you have set up an account, you can `fork the project <https://help.github.com/en/articles/fork-a-repo>`_
to create a copy of the repository that you can make changes to.

- Navigate to the `Funkwhale repository <https://dev.funkwhale.audio/funkwhale/funkwhale>`_
- Click "Fork" at the top of the repository
- You will be redirected to a new version of the project. This one's all yours!

.. _clone-repo:

Clone the Repository
^^^^^^^^^^^^^^^^^^^^

Once you have successfully forked the project, you can safely download a copy of this to your local
computer to create documents.

.. code-block:: shell

   # If you're using an SSH key

   git clone git@dev.funkwhale.audio:your-username/funkwhale.git

   # If you're using a username/password

   git clone https://dev.funkwhale.audio/your-username/funkwhale.git

Once you've cloned the repository, it's a good idea to create a new branch for your documents so that
you can :ref:`merge it later <merge-request>`

.. code-block:: shell

   # Create a new branch to make changes to

   git checkout -b [name_of_your_new_branch]

   # Push the branch up to your forked repository

   git push origin [name_of_your_new_branch]

.. _add-docs:

Add Documents to Your Branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you've got your repository all set up, you can start writing your documents. Remember to keep in mind
:doc:`who you are writing for <style>` when you are writing, and :doc:`check your syntax works <restructured>`.

Once you've written what you need to write, you can push these changes to your forked repository:

.. code-block:: shell

   # Add new documents to your commit

   git add [list your documents here]

   # Commit these to the branch

   git commit -m "Add a commit message here!"

   # Push the changes to your branch

   git push origin [name_of_your_new_branch]

.. _merge-request:

Create a Merge Request
^^^^^^^^^^^^^^^^^^^^^^

Once you've pushed all of your documents, you can create a `Merge Request <https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html>`_
to request the documents be merged into the official Funkwhale develop branch.

- Navigate to the `Funkwhale repository <https://dev.funkwhale.audio/funkwhale/funkwhale>`_
- Click "Merge Requests" on the left hand side
- Click on the "New Merge Request"
- Under the "Source Branch" select your forked repository and the branch to which you've pushed changes
- Under "Target Branch", select the "develop" branch
- Click "Compare Branches and Continue"
- In the form that comes up, provide a title/description of the changes you've made
- Click "Submit Merge Request" to submit

That's it! If your merge request is successful, you will get a notification from one of the maintainers letting
you know your changes have been accepted. Sometimes, you may need to make minor corrections. Don't worry! We'll
let you know what needs correcting.

