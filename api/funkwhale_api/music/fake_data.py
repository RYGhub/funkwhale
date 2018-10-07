"""
Populates the database with fake data
"""
import random

from funkwhale_api.music import factories


def create_data(count=25):
    artists = factories.ArtistFactory.create_batch(size=count)
    for artist in artists:
        print("Creating data for", artist)
        albums = factories.AlbumFactory.create_batch(
            artist=artist, size=random.randint(1, 5)
        )
        for album in albums:
            factories.UploadFactory.create_batch(
                track__album=album, size=random.randint(3, 18)
            )


if __name__ == "__main__":
    create_data()
