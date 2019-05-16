import random

from django.core.exceptions import ValidationError
from django.db import connection
from rest_framework import serializers
from taggit.models import Tag

from funkwhale_api.moderation import filters as moderation_filters
from funkwhale_api.music.models import Artist, Track
from funkwhale_api.users.models import User

from . import filters, models
from .registries import registry


class SimpleRadio(object):
    def clean(self, instance):
        return

    def pick(self, choices, previous_choices=[]):
        return random.sample(set(choices).difference(previous_choices), 1)[0]

    def pick_many(self, choices, quantity):
        return random.sample(set(choices), quantity)

    def weighted_pick(self, choices, previous_choices=[]):
        total = sum(weight for c, weight in choices)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices:
            if upto + weight >= r:
                return choice
            upto += weight


class SessionRadio(SimpleRadio):
    def __init__(self, session=None):
        self.session = session

    def start_session(self, user, **kwargs):
        self.session = models.RadioSession.objects.create(
            user=user, radio_type=self.radio_type, **kwargs
        )
        return self.session

    def get_queryset(self, **kwargs):
        qs = Track.objects.all()
        if not self.session:
            return qs
        if not self.session.user:
            return qs
        query = moderation_filters.get_filtered_content_query(
            config=moderation_filters.USER_FILTER_CONFIG["TRACK"],
            user=self.session.user,
        )
        return qs.exclude(query)

    def get_queryset_kwargs(self):
        return {}

    def get_choices(self, **kwargs):
        kwargs.update(self.get_queryset_kwargs())
        queryset = self.get_queryset(**kwargs)
        if self.session:
            queryset = self.filter_from_session(queryset)
            if kwargs.pop("filter_playable", True):
                queryset = queryset.playable_by(
                    self.session.user.actor if self.session.user else None
                )
        queryset = self.filter_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        return queryset

    def filter_from_session(self, queryset):
        already_played = self.session.session_tracks.all().values_list(
            "track", flat=True
        )
        queryset = queryset.exclude(pk__in=already_played)
        return queryset

    def pick(self, **kwargs):
        return self.pick_many(quantity=1, **kwargs)[0]

    def pick_many(self, quantity, **kwargs):
        choices = self.get_choices(**kwargs)
        picked_choices = super().pick_many(choices=choices, quantity=quantity)
        if self.session:
            for choice in picked_choices:
                self.session.add(choice)
        return picked_choices

    def validate_session(self, data, **context):
        return data


@registry.register(name="random")
class RandomRadio(SessionRadio):
    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.order_by("?")


@registry.register(name="favorites")
class FavoritesRadio(SessionRadio):
    def get_queryset_kwargs(self):
        kwargs = super().get_queryset_kwargs()
        if self.session:
            kwargs["user"] = self.session.user
        return kwargs

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        track_ids = kwargs["user"].track_favorites.all().values_list("track", flat=True)
        return qs.filter(pk__in=track_ids)


@registry.register(name="custom")
class CustomRadio(SessionRadio):
    def get_queryset_kwargs(self):
        kwargs = super().get_queryset_kwargs()
        kwargs["user"] = self.session.user
        kwargs["custom_radio"] = self.session.custom_radio
        return kwargs

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return filters.run(kwargs["custom_radio"].config, candidates=qs)

    def validate_session(self, data, **context):
        data = super().validate_session(data, **context)
        try:
            user = data["user"]
        except KeyError:
            user = context.get("user")
        try:
            assert data["custom_radio"].user == user or data["custom_radio"].is_public
        except KeyError:
            raise serializers.ValidationError("You must provide a custom radio")
        except AssertionError:
            raise serializers.ValidationError("You don't have access to this radio")
        return data


class RelatedObjectRadio(SessionRadio):
    """Abstract radio related to an object (tag, artist, user...)"""

    def clean(self, instance):
        super().clean(instance)
        if not instance.related_object:
            raise ValidationError(
                "Cannot start RelatedObjectRadio without related object"
            )
        if not isinstance(instance.related_object, self.model):
            raise ValidationError("Trying to start radio with bad related object")

    def get_related_object(self, pk):
        return self.model.objects.get(pk=pk)


@registry.register(name="tag")
class TagRadio(RelatedObjectRadio):
    model = Tag

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(tags__in=[self.session.related_object])


def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    assert False, "Shouldn't get here"


class NextNotFound(Exception):
    pass


@registry.register(name="similar")
class SimilarRadio(RelatedObjectRadio):
    model = Track

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        seeds = list(
            self.session.session_tracks.all()
            .values_list("track_id", flat=True)
            .order_by("-id")[:3]
        ) + [self.session.related_object.pk]
        for seed in seeds:
            try:
                return queryset.filter(pk=self.find_next_id(queryset, seed))
            except NextNotFound:
                continue

        return queryset.none()

    def find_next_id(self, queryset, seed):
        with connection.cursor() as cursor:
            query = """
            SELECT next, count(next) AS c
            FROM (
                SELECT
                    track_id,
                    creation_date,
                    LEAD(track_id) OVER (
                        PARTITION by user_id order by creation_date asc
                    ) AS next
                FROM history_listening
                INNER JOIN users_user ON (users_user.id = user_id)
                WHERE users_user.privacy_level = 'instance' OR users_user.privacy_level = 'everyone' OR user_id = %s
                ORDER BY creation_date ASC
            ) t WHERE track_id = %s AND next != %s GROUP BY next ORDER BY c DESC;
            """
            cursor.execute(query, [self.session.user_id, seed, seed])
            next_candidates = list(cursor.fetchall())

        if not next_candidates:
            raise NextNotFound()

        matching_tracks = list(
            queryset.filter(pk__in=[c[0] for c in next_candidates]).values_list(
                "id", flat=True
            )
        )
        next_candidates = [n for n in next_candidates if n[0] in matching_tracks]
        if not next_candidates:
            raise NextNotFound()
        return random.choice([c[0] for c in next_candidates])


@registry.register(name="artist")
class ArtistRadio(RelatedObjectRadio):
    model = Artist

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        return qs.filter(artist=self.session.related_object)


@registry.register(name="less-listened")
class LessListenedRadio(RelatedObjectRadio):
    model = User

    def clean(self, instance):
        instance.related_object = instance.user
        super().clean(instance)

    def get_queryset(self, **kwargs):
        qs = super().get_queryset(**kwargs)
        listened = self.session.user.listenings.all().values_list("track", flat=True)
        return qs.exclude(pk__in=listened).order_by("?")
