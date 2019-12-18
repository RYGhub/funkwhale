import collections

from django.contrib.contenttypes.models import ContentType

from . import models


def get_tags_from_foreign_key(
    ids, foreign_key_model, foreign_key_attr, tagged_items_attr="tagged_items"
):
    """
    Cf #988, this is useful to tag an artist with #Rock if all its tracks are tagged with
    #Rock, for instance.
    """
    data = {}
    objs = foreign_key_model.objects.filter(
        **{"{}__pk__in".format(foreign_key_attr): ids}
    ).order_by("-id")
    objs = objs.only("id", "{}_id".format(foreign_key_attr)).prefetch_related(
        tagged_items_attr
    )

    for obj in objs.iterator():
        # loop on all objects, store the objs tags + counter on the corresponding foreign key
        row_data = data.setdefault(
            getattr(obj, "{}_id".format(foreign_key_attr)),
            {"total_objs": 0, "tags": []},
        )
        row_data["total_objs"] += 1
        for ti in getattr(obj, tagged_items_attr).all():
            row_data["tags"].append(ti.tag_id)

    # now, keep only tags that are present on all objects, i.e tags where the count
    # matches total_objs
    final_data = {}
    for key, row_data in data.items():
        counter = collections.Counter(row_data["tags"])
        tags_to_keep = sorted(
            [t for t, c in counter.items() if c >= row_data["total_objs"]]
        )
        if tags_to_keep:
            final_data[key] = tags_to_keep
    return final_data


def add_tags_batch(data, model, tagged_items_attr="tagged_items"):
    model_ct = ContentType.objects.get_for_model(model)
    tagged_items = [
        models.TaggedItem(tag_id=tag_id, content_type=model_ct, object_id=obj_id)
        for obj_id, tag_ids in data.items()
        for tag_id in tag_ids
    ]

    return models.TaggedItem.objects.bulk_create(tagged_items, batch_size=2000)
