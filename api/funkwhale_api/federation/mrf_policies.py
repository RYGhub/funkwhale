from funkwhale_api.moderation import mrf


from . import activity


@mrf.inbox.register(name="instance_policies")
def instance_policies(payload, **kwargs):
    reject = activity.should_reject(
        fid=payload.get("id"),
        actor_id=kwargs.get("sender_id", payload.get("id")),
        payload=payload,
    )
    if reject:
        raise mrf.Discard()
