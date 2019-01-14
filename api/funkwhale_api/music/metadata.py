import base64
import datetime
import logging
import pendulum

import mutagen._util
import mutagen.oggtheora
import mutagen.oggvorbis
import mutagen.flac

from django import forms

logger = logging.getLogger(__name__)
NODEFAULT = object()


class TagNotFound(KeyError):
    pass


class UnsupportedTag(KeyError):
    pass


class ParseError(ValueError):
    pass


def get_id3_tag(f, k):
    if k == "pictures":
        return f.tags.getall("APIC")
    # First we try to grab the standard key
    possible_attributes = [("text", True), ("url", False)]
    for attr, select_first in possible_attributes:
        try:
            v = getattr(f.tags[k], attr)
            if select_first:
                v = v[0]
            return v
        except KeyError:
            break
        except AttributeError:
            continue

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


def clean_ogg_pictures(metadata_block_picture):
    pictures = []
    for b64_data in [metadata_block_picture]:

        try:
            data = base64.b64decode(b64_data)
        except (TypeError, ValueError):
            continue

        try:
            picture = mutagen.flac.Picture(data)
        except mutagen.flac.FLACError:
            continue

        pictures.append(
            {
                "mimetype": picture.mime,
                "content": picture.data,
                "description": "",
                "type": picture.type.real,
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


def convert_position(v):
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
            # sometimes, Picard leaves two uuids in the field, separated
            # by a slash or a ;
            value = value.split(";")[0].split("/")[0].strip()
        except (AttributeError, IndexError, TypeError):
            pass

        return super().to_python(value)


def get_date(value):
    ADDITIONAL_FORMATS = ["%Y-%d-%m %H:%M"]  # deezer date format
    try:
        parsed = pendulum.parse(str(value))
        return datetime.date(parsed.year, parsed.month, parsed.day)
    except pendulum.exceptions.ParserError:
        pass

    for date_format in ADDITIONAL_FORMATS:
        try:
            parsed = datetime.datetime.strptime(value, date_format)
        except ValueError:
            continue
        else:
            return datetime.date(parsed.year, parsed.month, parsed.day)

    raise ParseError("{} cannot be parsed as a date".format(value))


def split_and_return_first(separator):
    def inner(v):
        return v.split(separator)[0].strip()

    return inner


VALIDATION = {
    "musicbrainz_artistid": FirstUUIDField(),
    "musicbrainz_albumid": FirstUUIDField(),
    "musicbrainz_recordingid": FirstUUIDField(),
    "musicbrainz_albumartistid": FirstUUIDField(),
}

CONF = {
    "OggOpus": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_position,
            },
            "disc_number": {"field": "DISCNUMBER", "to_application": convert_position},
            "title": {},
            "artist": {},
            "album_artist": {
                "field": "albumartist",
                "to_application": split_and_return_first(";"),
            },
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
            "license": {},
            "copyright": {},
        },
    },
    "OggVorbis": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_position,
            },
            "disc_number": {"field": "DISCNUMBER", "to_application": convert_position},
            "title": {},
            "artist": {},
            "album_artist": {
                "field": "albumartist",
                "to_application": split_and_return_first(";"),
            },
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
            "license": {},
            "copyright": {},
            "pictures": {
                "field": "metadata_block_picture",
                "to_application": clean_ogg_pictures,
            },
        },
    },
    "OggTheora": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "track_number": {
                "field": "TRACKNUMBER",
                "to_application": convert_position,
            },
            "disc_number": {"field": "DISCNUMBER", "to_application": convert_position},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_albumartistid": {"field": "MusicBrainz Album Artist Id"},
            "musicbrainz_recordingid": {"field": "MusicBrainz Track Id"},
            "license": {},
            "copyright": {},
        },
    },
    "MP3": {
        "getter": get_id3_tag,
        "clean_pictures": clean_id3_pictures,
        "fields": {
            "track_number": {"field": "TRCK", "to_application": convert_position},
            "disc_number": {"field": "TPOS", "to_application": convert_position},
            "title": {"field": "TIT2"},
            "artist": {"field": "TPE1"},
            "album_artist": {"field": "TPE2"},
            "album": {"field": "TALB"},
            "date": {"field": "TDRC", "to_application": get_date},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_albumartistid": {"field": "MusicBrainz Album Artist Id"},
            "musicbrainz_recordingid": {
                "field": "UFID",
                "getter": get_mp3_recording_id,
            },
            "pictures": {},
            "license": {"field": "WCOP"},
            "copyright": {"field": "TCOP"},
        },
    },
    "FLAC": {
        "getter": get_flac_tag,
        "clean_pictures": clean_flac_pictures,
        "fields": {
            "track_number": {
                "field": "tracknumber",
                "to_application": convert_position,
            },
            "disc_number": {"field": "discnumber", "to_application": convert_position},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date", "to_application": get_date},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "musicbrainz_recordingid": {"field": "musicbrainz_trackid"},
            "test": {},
            "pictures": {},
            "license": {},
            "copyright": {},
        },
    },
}

ALL_FIELDS = [
    "track_number",
    "disc_number",
    "title",
    "artist",
    "album_artist",
    "album",
    "date",
    "musicbrainz_albumid",
    "musicbrainz_artistid",
    "musicbrainz_albumartistid",
    "musicbrainz_recordingid",
    "license",
    "copyright",
]


class Metadata(object):
    def __init__(self, filething, kind=mutagen.File):
        self._file = kind(filething)
        if self._file is None:
            raise ValueError("Cannot parse metadata from {}".format(filething))
        self.fallback = self.load_fallback(filething, self._file)
        ft = self.get_file_type(self._file)
        try:
            self._conf = CONF[ft]
        except KeyError:
            raise ValueError("Unsupported format {}".format(ft))

    def get_file_type(self, f):
        return f.__class__.__name__

    def load_fallback(self, filething, parent):
        """
        In some situations, such as Ogg Theora files tagged with MusicBrainz Picard,
        part of the tags are only available in the ogg vorbis comments
        """
        try:
            filething.seek(0)
        except AttributeError:
            pass
        if isinstance(parent, mutagen.oggtheora.OggTheora):
            try:
                return Metadata(filething, kind=mutagen.oggvorbis.OggVorbis)
            except (ValueError, mutagen._util.MutagenError):
                raise
                pass

    def get(self, key, default=NODEFAULT):
        try:
            return self._get_from_self(key)
        except TagNotFound:
            if not self.fallback:
                if default != NODEFAULT:
                    return default
                else:
                    raise
            else:
                return self.fallback.get(key, default=default)
        except UnsupportedTag:
            if not self.fallback:
                raise
            else:
                return self.fallback.get(key, default=default)

    def _get_from_self(self, key, default=NODEFAULT):
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

    def all(self, ignore_parse_errors=True):
        """
        Return a dict containing all metadata of the file
        """

        data = {}
        for field in ALL_FIELDS:
            try:
                data[field] = self.get(field, None)
            except (TagNotFound, forms.ValidationError):
                data[field] = None
            except ParseError as e:
                if not ignore_parse_errors:
                    raise
                logger.warning("Unparsable field {}: {}".format(field, str(e)))
                data[field] = None

        return data

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
