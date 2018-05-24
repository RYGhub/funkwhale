import django_filters

from funkwhale_api.common import fields

from . import models


class LibraryFilter(django_filters.FilterSet):
    approved = django_filters.BooleanFilter('following__approved')
    q = fields.SearchFilter(search_fields=[
        'actor__domain',
    ])

    class Meta:
        model = models.Library
        fields = {
            'approved': ['exact'],
            'federation_enabled': ['exact'],
            'download_files': ['exact'],
            'autoimport': ['exact'],
            'tracks_count': ['exact'],
        }


class LibraryTrackFilter(django_filters.FilterSet):
    library = django_filters.CharFilter('library__uuid')
    status = django_filters.CharFilter(method='filter_status')
    q = fields.SearchFilter(search_fields=[
        'artist_name',
        'title',
        'album_title',
        'library__actor__domain',
    ])

    def filter_status(self, queryset, field_name, value):
        if value == 'imported':
            return queryset.filter(local_track_file__isnull=False)
        elif value == 'not_imported':
            return queryset.filter(
                local_track_file__isnull=True
            ).exclude(import_jobs__status='pending')
        elif value == 'import_pending':
            return queryset.filter(import_jobs__status='pending')
        return queryset

    class Meta:
        model = models.LibraryTrack
        fields = {
            'library': ['exact'],
            'artist_name': ['exact', 'icontains'],
            'title': ['exact', 'icontains'],
            'album_title': ['exact', 'icontains'],
            'audio_mimetype': ['exact', 'icontains'],
        }


class FollowFilter(django_filters.FilterSet):
    pending = django_filters.CharFilter(method='filter_pending')
    ordering = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('creation_date', 'creation_date'),
            ('modification_date', 'modification_date'),
        ),
    )
    q = fields.SearchFilter(search_fields=[
        'actor__domain',
        'actor__preferred_username',
    ])

    class Meta:
        model = models.Follow
        fields = ['approved', 'pending', 'q']

    def filter_pending(self, queryset, field_name, value):
        if value.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(approved__isnull=True)
        return queryset
