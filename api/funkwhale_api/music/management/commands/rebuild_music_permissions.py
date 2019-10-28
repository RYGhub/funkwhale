from argparse import RawTextHelpFormatter

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from django.db import transaction
from django.db.models import Q

from funkwhale_api.music.models import TrackActor, Library
from funkwhale_api.federation.models import Actor


class Command(BaseCommand):
    help = """
    Rebuild audio permission table. You shouldn't have to do this by hand, but if you face
    any weird things (tracks still shown when they shouldn't, or tracks not shown when they should),
    this may help.

    """

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            nargs='*',
            help="Rebuild only for given users",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        actor_ids = []
        if options['username']:
            actors = Actor.objects.all().local(True)
            actor_ids = list(actors.filter(preferred_username__in=options['username']).values_list('id', flat=True))
            if len(actor_ids) < len(options['username']):
                raise CommandError('Invalid username')
            print('Emptying permission table for specified users…')
            qs = TrackActor.objects.all().filter(Q(actor__pk__in=actor_ids) | Q(actor=None))
            qs._raw_delete(qs.db)
        else:
            print('Emptying permission table…')
            qs = TrackActor.objects.all()
            qs._raw_delete(qs.db)
        libraries = Library.objects.all()
        objs = []
        total_libraries = len(libraries)
        for i, library in enumerate(libraries):
            print('[{}/{}] Populating permission table for library {}'.format(i + 1, total_libraries, library.pk))
            objs += TrackActor.get_objs(
                library=library,
                actor_ids=actor_ids,
                upload_and_track_ids=[],
            )
        print('Commiting changes…')
        TrackActor.objects.bulk_create(objs, batch_size=5000, ignore_conflicts=True)
