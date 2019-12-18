import pytest

from django.db import connection


@pytest.mark.parametrize(
    "factory_name,fields",
    [
        ("music.Artist", ["name"]),
        ("music.Album", ["title"]),
        ("music.Track", ["title"]),
    ],
)
def test_body_text_trigger_creation(factory_name, fields, factories):
    obj = factories[factory_name]()
    obj.refresh_from_db()
    cursor = connection.cursor()
    sql = """
        SELECT to_tsvector('english_nostop', '{indexed_text}')
    """.format(
        indexed_text=" ".join([getattr(obj, f) for f in fields if getattr(obj, f)]),
    )
    cursor.execute(sql)

    assert cursor.fetchone()[0] == obj.body_text


@pytest.mark.parametrize(
    "factory_name,fields",
    [
        ("music.Artist", ["name"]),
        ("music.Album", ["title"]),
        ("music.Track", ["title"]),
    ],
)
def test_body_text_trigger_updaten(factory_name, fields, factories, faker):
    obj = factories[factory_name]()
    for field in fields:
        setattr(obj, field, faker.sentence())
    obj.save()
    obj.refresh_from_db()
    cursor = connection.cursor()
    sql = """
        SELECT to_tsvector('english_nostop', '{indexed_text}')
    """.format(
        indexed_text=" ".join([getattr(obj, f) for f in fields if getattr(obj, f)]),
    )
    cursor.execute(sql)

    assert cursor.fetchone()[0] == obj.body_text
