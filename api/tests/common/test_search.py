import pytest

from django.db.models import Q
from django import forms

from funkwhale_api.common import search
from funkwhale_api.music import models as music_models


@pytest.mark.parametrize(
    "query,expected",
    [
        ("", [music_models.Album, music_models.Artist]),
        ("is:album", [music_models.Album]),
        ("is:artist is:album", [music_models.Artist, music_models.Album]),
    ],
)
def test_search_config_is(query, expected):
    s = search.SearchConfig(
        types=[("album", music_models.Album), ("artist", music_models.Artist)]
    )

    cleaned = s.clean(query)
    assert cleaned["types"] == expected


@pytest.mark.parametrize(
    "query,expected",
    [
        ("", None),
        ("hello world", search.get_query("hello world", ["f1", "f2", "f3"])),
        ("hello in:field2", search.get_query("hello", ["f2"])),
        ("hello in:field1,field2", search.get_query("hello", ["f1", "f2"])),
    ],
)
def test_search_config_query(query, expected):
    s = search.SearchConfig(
        search_fields={
            "field1": {"to": "f1"},
            "field2": {"to": "f2"},
            "field3": {"to": "f3"},
        }
    )

    cleaned = s.clean(query)
    assert cleaned["search_query"] == expected


def test_search_config_query_filter_field_handler():
    s = search.SearchConfig(
        filter_fields={"account": {"handler": lambda v: Q(hello="world")}}
    )

    cleaned = s.clean("account:noop")
    assert cleaned["filter_query"] == Q(hello="world")


def test_search_config_query_filter_field():
    s = search.SearchConfig(
        filter_fields={"account": {"to": "noop", "field": forms.BooleanField()}}
    )

    cleaned = s.clean("account:true")
    assert cleaned["filter_query"] == Q(noop=True)


@pytest.mark.parametrize(
    "query,expected",
    [
        ("", None),
        ("status:pending", Q(status="pending")),
        ('user:"silent bob"', Q(user__username__iexact="silent bob")),
        (
            "user:me status:pending",
            Q(user__username__iexact="me") & Q(status="pending"),
        ),
    ],
)
def test_search_config_filter(query, expected):
    s = search.SearchConfig(
        filter_fields={
            "user": {"to": "user__username__iexact"},
            "status": {"to": "status"},
        }
    )

    cleaned = s.clean(query)
    assert cleaned["filter_query"] == expected


def test_apply():
    cleaned = {
        "filter_query": Q(batch__submitted_by__username__iexact="me"),
        "search_query": Q(source="test"),
    }
    result = search.apply(music_models.ImportJob.objects.all(), cleaned)

    assert str(result.query) == str(
        music_models.ImportJob.objects.filter(
            Q(batch__submitted_by__username__iexact="me"), Q(source="test")
        ).query
    )
