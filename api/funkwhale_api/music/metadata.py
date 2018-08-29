import datetime
import mutagen
import pendulum
from django import forms

NODEFAULT = object()


class TagNotFound(KeyError):
    pass


class UnsupportedTag(KeyError):
    pass


def get_id3_tag(f, k):
    if k == "pictures":
        return f.tags.getall("APIC")
    # First we try to grab the standard key
    try:
        return f.tags[k].text[0]
    except KeyError:
        pass
    # then we fallback on parsing non standard tags
    all_tags = f.tags.getall("TXXX")
    try:
        matches = [t for t in all_tags if t.desc.lower() == k.lower()]
        return matches[0].text[0]
    except (KeyError, IndexError):
        raise TagNotFound(k)


def clean_id3_pictures(apic):
    pictures = []
    for p in list(apic):
        pictures.append(
            {
                "mimetype": p.mime,
                "content": p.data,
                "description": p.desc,
                "type": p.type.real,
            }
        )
    return pictures


def get_flac_tag(f, k):
    if k == "pictures":
        return f.pictures
    try:
        return f.get(k, [])[0]
    except (KeyError, IndexError):
        raise TagNotFound(k)


def clean_flac_pictures(apic):
    pictures = []
    for p in list(apic):
        pictures.append(
            {
                "mimetype": p.mime,
                "content": p.data,
                "description": p.desc,
                "type": p.type.real,
            }
        )
    return pictures


def get_mp3_recording_id(f, k):
    try:
        return [t for t in f.tags.getall("UFID") if "musicbrainz.org" in t.owner][
            0
        ].data.decode("utf-8")
    except IndexError:
        raise TagNotFound(k)


def convert_track_number(v):
    try:
        return int(v)
    except ValueError:
        # maybe the position is of the form "1/4"
        pass

    try:
        return int(v.split("/")[0])
    except (ValueError, AttributeError, IndexError):
        pass


class FirstUUIDField(forms.UUIDField):
    def to_python(self, value):
        try:
            # sometimes, Picard leaves to uuids in the field, separated
            # by a slash
            value = value.split("/")[0]
        except (AttributeError, IndexError, TypeError):
            pass

        return super().to_python(value)


def get_date(value):
    parsed = pendulum.parse(str(value))
    return datetime.date(parsed.year, parsed.month, parsed.day)


VALIDATION = {
    "musicbrainz_artistid": FirstUUIDField(),
    "musicbrainz_albumid": FirstUUIDField(),
    "musicbrainz_recordingid": FirstUUIDField(),
}

CONF = {
    "OggOpus": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_track_number,
            },
            "title": {},
            "artist": {},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
        },
    },
    "OggVorbis": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_track_number,
            },
            "title": {},
            "artist": {},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
        },
    },
    "OggTheora": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_track_number,
            },
            "title": {},
            "artist": {},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_recordingid": {"field": "MusicBrainz Track Id"},
        },
    },
    "MP3": {
        "getter": get_id3_tag,
        "clean_pictures": clean_id3_pictures,
        "fields": {
            "track_number": {"field": "TRCK", "to_application": convert_track_number},
            "title": {"field": "TIT2"},
            "artist": {"field": "TPE1"},
            "album": {"field": "TALB"},
            "date": {"field": "TDRC", "to_application": get_date},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_recordingid": {
                "field": "UFID",
                "getter": get_mp3_recording_id,
            },
            "pictures": {},
        },
    },
    "FLAC": {
        "getter": get_flac_tag,
        "clean_pictures": clean_flac_pictures,
        "fields": {
            "track_number": {
                "field": "tracknumber",
                "to_application": convert_track_number,
            },
            "title": {},
            "artist": {},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
            "test": {},
            "pictures": {},
        },
    },
}


class Metadata(object):
    def __init__(self, path):
        self._file = mutagen.File(path)
        if self._file is None:
            raise ValueError("Cannot parse metadata from {}".format(path))
        ft = self.get_file_type(self._file)
        try:
            self._conf = CONF[ft]
        except KeyError:
            raise ValueError("Unsupported format {}".format(ft))

    def get_file_type(self, f):
        return f.__class__.__name__

    def get(self, key, default=NODEFAULT):
        try:
            field_conf = self._conf["fields"][key]
        except KeyError:
            raise UnsupportedTag("{} is not supported for this file format".format(key))
        real_key = field_conf.get("field", key)
        try:
            getter = field_conf.get("getter", self._conf["getter"])
            v = getter(self._file, real_key)
        except KeyError:
            if default == NODEFAULT:
                raise TagNotFound(real_key)
            return default

        converter = field_conf.get("to_application")
        if converter:
            v = converter(v)
        field = VALIDATION.get(key)
        if field:
            v = field.to_python(v)
        return v

    def get_picture(self, picture_type="cover_front"):
        ptype = getattr(mutagen.id3.PictureType, picture_type.upper())
        try:
            pictures = self.get("pictures")
        except (UnsupportedTag, TagNotFound):
            return

        cleaner = self._conf.get("clean_pictures", lambda v: v)
        pictures = cleaner(pictures)
        for p in pictures:
            if p["type"] == ptype:
                return p
