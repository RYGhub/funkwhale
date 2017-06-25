import random
from django.core.exceptions import ValidationError
from taggit.models import Tag
from funkwhale_api.users.models import User
from funkwhale_api.music.models import Track, Artist
from . import models
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
        self.session = models.RadioSession.objects.create(user=user, radio_type=self.radio_type, **kwargs)
        return self.session

    def get_queryset(self):
        raise NotImplementedError

    def get_queryset_kwargs(self):
        return {}

    def get_choices(self, **kwargs):
        kwargs.update(self.get_queryset_kwargs())
        queryset = self.get_queryset(**kwargs)
        if self.session:
            queryset = self.filter_from_session(queryset)
        return queryset

    def filter_from_session(self, queryset):
        already_played = self.session.session_tracks.all().values_list('track', flat=True)
        queryset = queryset.exclude(pk__in=list(already_played))
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

@registry.register(name='random')
class RandomRadio(SessionRadio):
    def get_queryset(self, **kwargs):
        return Track.objects.all()

@registry.register(name='favorites')
class FavoritesRadio(SessionRadio):

    def get_queryset_kwargs(self):
        kwargs = super().get_queryset_kwargs()
        if self.session:
            kwargs['user'] = self.session.user
        return kwargs

    def get_queryset(self, **kwargs):
        track_ids = kwargs['user'].track_favorites.all().values_list('track', flat=True)
        return Track.objects.filter(pk__in=track_ids)


class RelatedObjectRadio(SessionRadio):
    """Abstract radio related to an object (tag, artist, user...)"""

    def clean(self, instance):
        super().clean(instance)
        if not instance.related_object:
            raise ValidationError('Cannot start RelatedObjectRadio without related object')
        if not isinstance(instance.related_object, self.model):
            raise ValidationError('Trying to start radio with bad related object')

    def get_related_object(self, pk):
        return self.model.objects.get(pk=pk)


@registry.register(name='tag')
class TagRadio(RelatedObjectRadio):
    model = Tag

    def get_queryset(self, **kwargs):
        return Track.objects.filter(tags__in=[self.session.related_object])

@registry.register(name='artist')
class ArtistRadio(RelatedObjectRadio):
    model = Artist

    def get_queryset(self, **kwargs):
        return self.session.related_object.tracks.all()


@registry.register(name='less-listened')
class LessListenedRadio(RelatedObjectRadio):
    model = User

    def clean(self, instance):
        instance.related_object = instance.user
        super().clean(instance)

    def get_queryset(self, **kwargs):
        listened = self.session.user.listenings.all().values_list('track', flat=True)
        return Track.objects.exclude(pk__in=listened).order_by('?')
