import click

from funkwhale_api.music import tasks

from . import base


def handler_add_tags_from_tracks(
    artists=False, albums=False,
):
    result = None
    if artists:
        result = tasks.artists_set_tags_from_tracks()
    elif albums:
        result = tasks.albums_set_tags_from_tracks()
    else:
        raise click.BadOptionUsage("You must specify artists or albums")

    if result is None:
        click.echo("  No relevant tags found")
    else:
        click.echo("  Relevant tags added to {} objects".format(len(result)))


@base.cli.group()
def albums():
    """Manage albums"""
    pass


@base.cli.group()
def artists():
    """Manage artists"""
    pass


@albums.command(name="add-tags-from-tracks")
def albums_add_tags_from_tracks():
    """
    Associate tags to album with no genre tags, assuming identical tags are found on the album tracks
    """
    handler_add_tags_from_tracks(albums=True)


@artists.command(name="add-tags-from-tracks")
def artists_add_tags_from_tracks():
    """
    Associate tags to artists with no genre tags, assuming identical tags are found on the artist tracks
    """
    handler_add_tags_from_tracks(artists=True)
