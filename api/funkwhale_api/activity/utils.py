from django.db import models

from funkwhale_api.common import fields
from funkwhale_api.favorites.models import TrackFavorite
from funkwhale_api.history.models import Listening


def combined_recent(limit, **kwargs):
    datetime_field = kwargs.pop("datetime_field", "creation_date")
    source_querysets = {qs.model._meta.label: qs for qs in kwargs.pop("querysets")}
    querysets = {
        k: qs.annotate(
            __type=models.Value(qs.model._meta.label, output_field=models.CharField())
        ).values("pk", datetime_field, "__type")
        for k, qs in source_querysets.items()
    }
    _qs_list = list(querysets.values())
    union_qs = _qs_list[0].union(*_qs_list[1:])
    records = []
    for row in union_qs.order_by("-{}".format(datetime_field))[:limit]:
        records.append(
            {"type": row["__type"], "when": row[datetime_field], "pk": row["pk"]}
        )
    # Now we bulk-load each object type in turn
    to_load = {}
    for record in records:
        to_load.setdefault(record["type"], []).append(record["pk"])
    fetched = {}

    for key, pks in to_load.items():
        for item in source_querysets[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item

    # Annotate 'records' with loaded objects
    for record in records:
        record["object"] = fetched[(record["type"], record["pk"])]
    return records


def get_activity(user, limit=20):
    query = fields.privacy_level_query(user, lookup_field="user__privacy_level")
    querysets = [
        Listening.objects.filter(query).select_related(
            "track", "user", "track__artist", "track__album__artist"
        ),
        TrackFavorite.objects.filter(query).select_related(
            "track", "user", "track__artist", "track__album__artist"
        ),
    ]
    records = combined_recent(limit=limit, querysets=querysets)
    return [r["object"] for r in records]
