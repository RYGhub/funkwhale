import uuid

from django.db import transaction

from funkwhale_api.common import mutations
from funkwhale_api.common import utils
from funkwhale_api.federation import models

from . import tasks


@mutations.registry.connect("delete_account", models.Actor)
class DeleteAccountMutationSerializer(mutations.MutationSerializer):
    @transaction.atomic
    def apply(self, obj, validated_data):
        if not obj.is_local or not obj.user:
            raise mutations.serializers.ValidationError("Cannot delete this account")

        # delete oauth apps / reset all passwords immediatly
        obj.user.set_unusable_password()
        obj.user.subsonic_api_token = None
        # force logout
        obj.user.secret_key = uuid.uuid4()
        obj.user.users_grant.all().delete()
        obj.user.users_accesstoken.all().delete()
        obj.user.users_refreshtoken.all().delete()
        obj.user.save()

        # since the deletion of related object/message sending  can take a long time
        # we do that in a separate tasks
        utils.on_commit(tasks.delete_account.delay, user_id=obj.user.id)

    def get_previous_state(self, obj, validated_data):
        """
        We store usernames and ids for auditability purposes
        """
        return {
            "user": {"username": obj.user.username, "id": obj.user.pk},
            "actor": {"preferred_username": obj.preferred_username},
        }
