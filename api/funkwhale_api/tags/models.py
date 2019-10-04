import re

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import CICharField
from django.db import models
from django.db import transaction

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


TAG_REGEX = re.compile(r"^((\w+)([\d_]*))$")


class Tag(models.Model):
    name = CICharField(max_length=100, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class TaggedItemQuerySet(models.QuerySet):
    def for_content_object(self, obj):
        return self.filter(
            object_id=obj.id,
            content_type__app_label=obj._meta.app_label,
            content_type__model=obj._meta.model_name,
        )


class TaggedItem(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    tag = models.ForeignKey(Tag, related_name="tagged_items", on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
        related_name="tagged_items",
    )
    object_id = models.IntegerField(verbose_name=_("Object id"), db_index=True)
    content_object = GenericForeignKey()

    objects = TaggedItemQuerySet.as_manager()

    class Meta:
        unique_together = ("tag", "content_type", "object_id")


@transaction.atomic
def add_tags(obj, *tags):
    if not tags:
        return
    tag_objs = [Tag(name=t) for t in tags]
    Tag.objects.bulk_create(tag_objs, ignore_conflicts=True)
    tag_ids = Tag.objects.filter(name__in=tags).values_list("id", flat=True)

    tagged_items = [TaggedItem(tag_id=tag_id, content_object=obj) for tag_id in tag_ids]

    TaggedItem.objects.bulk_create(tagged_items, ignore_conflicts=True)


@transaction.atomic
def set_tags(obj, *tags):
    # we ignore any extra tags if the length of the list is higher
    # than our accepted size
    tags = tags[: settings.TAGS_MAX_BY_OBJ]
    tags = set(tags)
    existing = set(
        TaggedItem.objects.for_content_object(obj).values_list("tag__name", flat=True)
    )
    found = tags & existing
    to_add = tags - found
    to_remove = existing - (found | to_add)

    add_tags(obj, *to_add)
    remove_tags(obj, *to_remove)


@transaction.atomic
def remove_tags(obj, *tags):
    if not tags:
        return
    TaggedItem.objects.for_content_object(obj).filter(tag__name__in=tags).delete()
