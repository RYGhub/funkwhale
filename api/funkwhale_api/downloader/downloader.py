import os

import youtube_dl
from django.conf import settings


def download(
    url, target_directory=settings.MEDIA_ROOT, name="%(id)s.%(ext)s", bitrate=192
):
    target_path = os.path.join(target_directory, name)
    ydl_opts = {
        "quiet": True,
        "outtmpl": target_path,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "vorbis"}],
    }
    _downloader = youtube_dl.YoutubeDL(ydl_opts)
    info = _downloader.extract_info(url)
    info["audio_file_path"] = target_path % {"id": info["id"], "ext": "ogg"}
    return info
