import logging

from django.db.models.deletion import Collector

from funkwhale_api.federation import routes
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

    # Then we broadcast the info over federation. We do this *before* deleting objects
    # associated with the actor, otherwise follows are removed and we don't know where
    # to broadcast
    logger.info("Broadcasting deletion to federation…")
    routes.outbox.dispatch(
        {"type": "Delete", "object": {"type": actor.type}}, context={"actor": actor}
    )

    # then we delete any object associated with the actor object, but *not* the actor
    # itself. We keep it for auditability and sending the Delete ActivityPub message
    collector = Collector(using="default")
    logger.info(
        "Prepare deletion of objects associated with account %s…", user.username
    )
    collector.collect([actor])

    for model, instances in collector.data.items():
        if issubclass(model, actor.__class__):
            # we skip deletion of the actor itself
            continue

        logger.info(
            "Deleting %s objects associated with account %s…",
            len(instances),
            user.username,
        )
        to_delete = model.objects.filter(pk__in=[instance.pk for instance in instances])
        to_delete.delete()

    # Finally, we update the actor itself and mark it as removed
    logger.info("Marking actor as Tombsone…")
    actor.type = "Tombstone"
    actor.name = None
    actor.summary = None
    actor.save(update_fields=["type", "name", "summary"])
    logger.info("Deletion of account done %s!", user.username)
