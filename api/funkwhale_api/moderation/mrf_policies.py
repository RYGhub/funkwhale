import urllib.parse

from funkwhale_api.common import preferences
from funkwhale_api.common import utils
from funkwhale_api.federation import models as federation_models
from funkwhale_api.moderation import mrf


@mrf.inbox.register(name="allow_list")
def check_allow_list(payload, **kwargs):
    """
    A MRF policy that only works when the moderation__allow_list_enabled
    setting is on.

    It will extract domain names from the activity ID, actor ID and activity object ID
    and discard the activity if any of those domain names isn't on the allow list.
    """
    if not preferences.get("moderation__allow_list_enabled"):
        raise mrf.Skip("Allow-listing is disabled")

    allowed_domains = set(
        federation_models.Domain.objects.filter(allowed=True).values_list(
            "name", flat=True
        )
    )

    relevant_ids = [
        payload.get("actor"),
        kwargs.get("sender_id", payload.get("id")),
        utils.recursive_getattr(payload, "object.id", permissive=True),
    ]

    relevant_domains = set(
        [
            domain
            for domain in [urllib.parse.urlparse(i).hostname for i in relevant_ids if i]
            if domain
        ]
    )

    if relevant_domains - allowed_domains:

        raise mrf.Discard(
            "These domains are not allowed: {}".format(
                ", ".join(relevant_domains - allowed_domains)
            )
        )
