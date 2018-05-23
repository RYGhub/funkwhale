from django import forms
import arrow
import mutagen

NODEFAULT = object()


class TagNotFound(KeyError):
    pass


def get_id3_tag(f, k):
    # First we try to grab the standard key
    try:
        return f.tags[k].text[0]
    except KeyError:
        pass
    # then we fallback on parsing non standard tags
    all_tags = f.tags.getall('TXXX')
    try:
        matches = [
            t
            for t in all_tags
            if t.desc.lower() == k.lower()
        ]
        return matches[0].text[0]
    except (KeyError, IndexError):
        raise TagNotFound(k)


def get_flac_tag(f, k):
    try:
        return f.get(k, [])[0]
    except (KeyError, IndexError):
        raise TagNotFound(k)


def get_mp3_recording_id(f, k):
    try:
        return [
            t
            for t in f.tags.getall('UFID')
            if 'musicbrainz.org' in t.owner
        ][0].data.decode('utf-8')
    except IndexError:
        raise TagNotFound(k)


def convert_track_number(v):
    try:
        return int(v)
    except ValueError:
        # maybe the position is of the form "1/4"
        pass

    try:
        return int(v.split('/')[0])
    except (ValueError, AttributeError, IndexError):
        pass


VALIDATION = {
    'musicbrainz_artistid': forms.UUIDField(),
    'musicbrainz_albumid': forms.UUIDField(),
    'musicbrainz_recordingid': forms.UUIDField(),
}

CONF = {
    'OggVorbis': {
        'getter': lambda f, k: f[k][0],
        'fields': {
            'track_number': {
                'field': 'TRACKNUMBER',
                'to_application': convert_track_number
            },
            'title': {
                'field': 'title'
            },
            'artist': {
                'field': 'artist'
            },
            'album': {
                'field': 'album'
            },
            'date': {
                'field': 'date',
                'to_application': lambda v: arrow.get(v).date()
            },
            'musicbrainz_albumid': {
                'field': 'musicbrainz_albumid'
            },
            'musicbrainz_artistid': {
                'field': 'musicbrainz_artistid'
            },
            'musicbrainz_recordingid': {
                'field': 'musicbrainz_trackid'
            },
        }
    },
    'OggTheora': {
        'getter': lambda f, k: f[k][0],
        'fields': {
            'track_number': {
                'field': 'TRACKNUMBER',
                'to_application': convert_track_number
            },
            'title': {
                'field': 'title'
            },
            'artist': {
                'field': 'artist'
            },
            'album': {
                'field': 'album'
            },
            'date': {
                'field': 'date',
                'to_application': lambda v: arrow.get(v).date()
            },
            'musicbrainz_albumid': {
                'field': 'musicbrainz_albumid'
            },
            'musicbrainz_artistid': {
                'field': 'musicbrainz_artistid'
            },
            'musicbrainz_recordingid': {
                'field': 'musicbrainz_trackid'
            },
        }
    },
    'MP3': {
        'getter': get_id3_tag,
        'fields': {
            'track_number': {
                'field': 'TPOS',
                'to_application': convert_track_number
            },
            'title': {
                'field': 'TIT2'
            },
            'artist': {
                'field': 'TPE1'
            },
            'album': {
                'field': 'TALB'
            },
            'date': {
                'field': 'TDRC',
                'to_application': lambda v: arrow.get(str(v)).date()
            },
            'musicbrainz_albumid': {
                'field': 'MusicBrainz Album Id'
            },
            'musicbrainz_artistid': {
                'field': 'MusicBrainz Artist Id'
            },
            'musicbrainz_recordingid': {
                'field': 'UFID',
                'getter': get_mp3_recording_id,
            },
        }
    },
    'FLAC': {
        'getter': get_flac_tag,
        'fields': {
            'track_number': {
                'field': 'tracknumber',
                'to_application': convert_track_number
            },
            'title': {
                'field': 'title'
            },
            'artist': {
                'field': 'artist'
            },
            'album': {
                'field': 'album'
            },
            'date': {
                'field': 'date',
                'to_application': lambda v: arrow.get(str(v)).date()
            },
            'musicbrainz_albumid': {
                'field': 'musicbrainz_albumid'
            },
            'musicbrainz_artistid': {
                'field': 'musicbrainz_artistid'
            },
            'musicbrainz_recordingid': {
                'field': 'musicbrainz_trackid'
            },
            'test': {
                'field': 'test'
            },
        }
    },
}


class Metadata(object):

    def __init__(self, path):
        self._file = mutagen.File(path)
        if self._file is None:
            raise ValueError('Cannot parse metadata from {}'.format(path))
        ft = self.get_file_type(self._file)
        try:
            self._conf = CONF[ft]
        except KeyError:
            raise ValueError('Unsupported format {}'.format(ft))

    def get_file_type(self, f):
        return f.__class__.__name__

    def get(self, key, default=NODEFAULT):
        field_conf = self._conf['fields'][key]
        real_key = field_conf['field']
        try:
            getter = field_conf.get('getter', self._conf['getter'])
            v = getter(self._file, real_key)
        except KeyError:
            if default == NODEFAULT:
                raise TagNotFound(real_key)
            return default

        converter = field_conf.get('to_application')
        if converter:
            v = converter(v)
        field = VALIDATION.get(key)
        if field:
            v = field.to_python(v)
        return v
