import logging

from funkwhale_api.federation import tasks as federation_tasks
from funkwhale_api.taskapp import celery

from . import models

logger = logging.getLogger(__name__)


@celery.app.task(name="users.delete_account")
@celery.require_instance(models.User.objects.select_related("actor"), "user")
def delete_account(user):
    logger.info("Starting deletion of account %s…", user.username)
    actor = user.actor
    # we start by deleting the user obj, which will cascade deletion
    # to any other object
    user.delete()
    logger.info("Deleted user object")

    # ensure actor is set to tombstone, activities are removed, etc.
    federation_tasks.remove_actor(actor_id=actor.pk)
    logger.info("Deletion of account done %s!", actor.preferred_username)
