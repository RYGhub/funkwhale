def test_channel(factories, now):
    channel = factories["audio.Channel"]()
    assert channel.artist is not None
    assert channel.actor is not None
    assert channel.attributed_to is not None
    assert channel.library is not None
    assert channel.creation_date >= now
