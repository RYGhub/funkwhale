"""
Compute different sizes of image used for Album covers and User avatars
"""

from funkwhale_api.music.models import Upload


def main(command, **kwargs):
    queryset = Upload.objects.filter(
        source__startswith="http", source__contains="/federation/music/file/"
    ).exclude(source__contains="youtube")
    total = queryset.count()
    command.stdout.write("{} uploads found".format(total))
    queryset.delete()
