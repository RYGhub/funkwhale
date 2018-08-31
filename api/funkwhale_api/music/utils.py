import mimetypes

import magic
import mutagen

from funkwhale_api.common.search import normalize_query, get_query  # noqa


def guess_mimetype(f):
    b = min(1000000, f.size)
    t = magic.from_buffer(f.read(b), mime=True)
    if not t.startswith("audio/"):
        # failure, we try guessing by extension
        mt, _ = mimetypes.guess_type(f.path)
        if mt:
            t = mt
    return t


def compute_status(jobs):
    statuses = jobs.order_by().values_list("status", flat=True).distinct()
    errored = any([status == "errored" for status in statuses])
    if errored:
        return "errored"
    pending = any([status == "pending" for status in statuses])
    if pending:
        return "pending"
    return "finished"


AUDIO_EXTENSIONS_AND_MIMETYPE = [
    ("ogg", "audio/ogg"),
    ("mp3", "audio/mpeg"),
    ("flac", "audio/x-flac"),
]

EXTENSION_TO_MIMETYPE = {ext: mt for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}
MIMETYPE_TO_EXTENSION = {mt: ext for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}


def get_ext_from_type(mimetype):
    return MIMETYPE_TO_EXTENSION.get(mimetype)


def get_type_from_ext(extension):
    if extension.startswith("."):
        # we remove leading dot
        extension = extension[1:]
    return EXTENSION_TO_MIMETYPE.get(extension)


def get_audio_file_data(f):
    data = mutagen.File(f)
    if not data:
        return
    d = {}
    d["bitrate"] = getattr(data.info, "bitrate", 0)
    d["length"] = data.info.length

    return d
