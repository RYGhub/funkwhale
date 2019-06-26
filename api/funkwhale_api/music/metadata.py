import base64
import datetime
import logging
import pendulum

import mutagen._util
import mutagen.oggtheora
import mutagen.oggvorbis
import mutagen.flac

from rest_framework import serializers
from rest_framework.compat import Mapping

logger = logging.getLogger(__name__)
NODEFAULT = object()
# default title used when imported tracks miss the `Album` tag, see #122
UNKWOWN_ALBUM = "[Unknown Album]"


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


VALIDATION = {}

CONF = {
    "OggOpus": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "position": {"field": "TRACKNUMBER"},
            "disc_number": {"field": "DISCNUMBER"},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date"},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "mbid": {"field": "musicbrainz_trackid"},
            "license": {},
            "copyright": {},
        },
    },
    "OggVorbis": {
        "getter": lambda f, k: f[k][0],
        "fields": {
            "position": {"field": "TRACKNUMBER"},
            "disc_number": {"field": "DISCNUMBER"},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date"},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "mbid": {"field": "musicbrainz_trackid"},
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
            "position": {"field": "TRACKNUMBER"},
            "disc_number": {"field": "DISCNUMBER"},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date"},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_albumartistid": {"field": "MusicBrainz Album Artist Id"},
            "mbid": {"field": "MusicBrainz Track Id"},
            "license": {},
            "copyright": {},
        },
    },
    "MP3": {
        "getter": get_id3_tag,
        "clean_pictures": clean_id3_pictures,
        "fields": {
            "position": {"field": "TRCK"},
            "disc_number": {"field": "TPOS"},
            "title": {"field": "TIT2"},
            "artist": {"field": "TPE1"},
            "album_artist": {"field": "TPE2"},
            "album": {"field": "TALB"},
            "date": {"field": "TDRC"},
            "musicbrainz_albumid": {"field": "MusicBrainz Album Id"},
            "musicbrainz_artistid": {"field": "MusicBrainz Artist Id"},
            "musicbrainz_albumartistid": {"field": "MusicBrainz Album Artist Id"},
            "mbid": {"field": "UFID", "getter": get_mp3_recording_id},
            "pictures": {},
            "license": {"field": "WCOP"},
            "copyright": {"field": "TCOP"},
        },
    },
    "FLAC": {
        "getter": get_flac_tag,
        "clean_pictures": clean_flac_pictures,
        "fields": {
            "position": {"field": "tracknumber"},
            "disc_number": {"field": "discnumber"},
            "title": {},
            "artist": {},
            "album_artist": {"field": "albumartist"},
            "album": {},
            "date": {"field": "date"},
            "musicbrainz_albumid": {},
            "musicbrainz_artistid": {},
            "musicbrainz_albumartistid": {},
            "mbid": {"field": "musicbrainz_trackid"},
            "test": {},
            "pictures": {},
            "license": {},
            "copyright": {},
        },
    },
}

ALL_FIELDS = [
    "position",
    "disc_number",
    "title",
    "artist",
    "album_artist",
    "album",
    "date",
    "musicbrainz_albumid",
    "musicbrainz_artistid",
    "musicbrainz_albumartistid",
    "mbid",
    "license",
    "copyright",
]


class Metadata(Mapping):
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

    def all(self):
        """
        Return a dict with all support metadata fields, if they are available
        """
        final = {}
        for field in self._conf["fields"]:
            if field in ["pictures"]:
                continue
            value = self.get(field, None)
            if value is None:
                continue
            final[field] = str(value)

        return final

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

    def get_picture(self, *picture_types):
        if not picture_types:
            raise ValueError("You need to request at least one picture type")
        ptypes = [
            getattr(mutagen.id3.PictureType, picture_type.upper())
            for picture_type in picture_types
        ]

        try:
            pictures = self.get("pictures")
        except (UnsupportedTag, TagNotFound):
            return

        cleaner = self._conf.get("clean_pictures", lambda v: v)
        pictures = cleaner(pictures)
        if not pictures:
            return
        for ptype in ptypes:
            for p in pictures:
                if p["type"] == ptype:
                    return p

    def __getitem__(self, key):
        return self.get(key)

    def __len__(self):
        return 1

    def __iter__(self):
        for field in self._conf["fields"]:
            yield field


class ArtistField(serializers.Field):
    def __init__(self, *args, **kwargs):
        self.for_album = kwargs.pop("for_album", False)
        super().__init__(*args, **kwargs)

    def get_value(self, data):
        if self.for_album:
            keys = [("names", "album_artist"), ("mbids", "musicbrainz_albumartistid")]
        else:
            keys = [("names", "artist"), ("mbids", "musicbrainz_artistid")]

        final = {}
        for field, key in keys:
            final[field] = data.get(key, None)

        return final

    def to_internal_value(self, data):
        # we have multiple values that can be separated by various separators
        separators = [";"]
        # we get a list like that if tagged via musicbrainz
        # ae29aae4-abfb-4609-8f54-417b1f4d64cc; 3237b5a8-ae44-400c-aa6d-cea51f0b9074;
        raw_mbids = data["mbids"]
        used_separator = None
        mbids = [raw_mbids]
        if raw_mbids:
            if "/" in raw_mbids:
                # it's a featuring, we can't handle this now
                mbids = []
            else:
                for separator in separators:
                    if separator in raw_mbids:
                        used_separator = separator
                        mbids = [m.strip() for m in raw_mbids.split(separator)]
                        break

        # now, we split on artist names, using the same separator as the one used
        # by mbids, if any
        if used_separator and mbids:
            names = [n.strip() for n in data["names"].split(used_separator)]
        else:
            names = [data["names"]]

        final = []
        for i, name in enumerate(names):
            try:
                mbid = mbids[i]
            except IndexError:
                mbid = None
            artist = {"name": name, "mbid": mbid}
            final.append(artist)

        field = serializers.ListField(child=ArtistSerializer(), min_length=1)

        return field.to_internal_value(final)


class AlbumField(serializers.Field):
    def get_value(self, data):
        return data

    def to_internal_value(self, data):
        try:
            title = data.get("album") or ""
        except TagNotFound:
            title = ""

        title = title.strip() or UNKWOWN_ALBUM
        final = {
            "title": title,
            "release_date": data.get("date", None),
            "mbid": data.get("musicbrainz_albumid", None),
        }
        artists_field = ArtistField(for_album=True)
        payload = artists_field.get_value(data)
        try:
            artists = artists_field.to_internal_value(payload)
        except serializers.ValidationError as e:
            artists = []
            logger.debug("Ignoring validation error on album artists: %s", e)
        album_serializer = AlbumSerializer(data=final)
        album_serializer.is_valid(raise_exception=True)
        album_serializer.validated_data["artists"] = artists
        return album_serializer.validated_data


class CoverDataField(serializers.Field):
    def get_value(self, data):
        return data

    def to_internal_value(self, data):
        return data.get_picture("cover_front", "other")


class PermissiveDateField(serializers.CharField):
    def to_internal_value(self, value):
        if not value:
            return None
        value = super().to_internal_value(str(value))
        ADDITIONAL_FORMATS = [
            "%Y-%d-%m %H:%M",  # deezer date format
            "%Y-%W",  # weird date format based on week number, see #718
        ]

        for date_format in ADDITIONAL_FORMATS:
            try:
                parsed = datetime.datetime.strptime(value, date_format)
            except ValueError:
                continue
            else:
                return datetime.date(parsed.year, parsed.month, parsed.day)

        try:
            parsed = pendulum.parse(str(value))
            return datetime.date(parsed.year, parsed.month, parsed.day)
        except pendulum.exceptions.ParserError:
            pass

        return None


class MBIDField(serializers.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("allow_null", True)
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, v):
        if v in ["", None]:
            return None
        return super().to_internal_value(v)


class ArtistSerializer(serializers.Serializer):
    name = serializers.CharField()
    mbid = MBIDField()


class AlbumSerializer(serializers.Serializer):
    title = serializers.CharField()
    mbid = MBIDField()
    release_date = PermissiveDateField(required=False, allow_null=True)


class PositionField(serializers.CharField):
    def to_internal_value(self, v):
        v = super().to_internal_value(v)
        if not v:
            return v

        try:
            return int(v)
        except ValueError:
            # maybe the position is of the form "1/4"
            pass

        try:
            return int(v.split("/")[0])
        except (ValueError, AttributeError, IndexError):
            pass


class TrackMetadataSerializer(serializers.Serializer):
    title = serializers.CharField()
    position = PositionField(allow_blank=True, allow_null=True, required=False)
    disc_number = PositionField(allow_blank=True, allow_null=True, required=False)
    copyright = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    license = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    mbid = MBIDField()

    album = AlbumField()
    artists = ArtistField()
    cover_data = CoverDataField()

    remove_blank_null_fields = [
        "copyright",
        "license",
        "position",
        "disc_number",
        "mbid",
    ]

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        for field in self.remove_blank_null_fields:
            try:
                v = validated_data[field]
            except KeyError:
                continue
            if v in ["", None]:
                validated_data.pop(field)
        return validated_data


class FakeMetadata(Mapping):
    def __init__(self, data, picture=None):
        self.data = data
        self.picture = None

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def get_picture(self, *args):
        return self.picture
