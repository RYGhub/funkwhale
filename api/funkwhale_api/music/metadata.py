import mutagen

NODEFAULT = object()

class Metadata(object):
    ALIASES = {
        'release': 'musicbrainz_albumid',
        'artist': 'musicbrainz_artistid',
        'recording': 'musicbrainz_trackid',
    }

    def __init__(self, path):
        self._file = mutagen.File(path)

    def get(self, key, default=NODEFAULT, single=True):
        try:
            v = self._file[key]
        except KeyError:
            if default == NODEFAULT:
                raise
            return default

        # Some tags are returned as lists of string
        if single:
            return v[0]
        return v

    def __getattr__(self, key):
        try:
            alias = self.ALIASES[key]
        except KeyError:
            raise ValueError('Invalid alias {}'.format(key))

        return self.get(alias, single=True)
