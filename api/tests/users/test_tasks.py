import pytest

from funkwhale_api.federation import routes
from funkwhale_api.users import tasks


def test_delete_account(factories, mocker):
    user = factories["users.User"]()
    actor = user.create_actor()
    factories["federation.Follow"](target=actor, approved=True)
    library = factories["music.Library"](actor=actor)
    unrelated_library = factories["music.Library"]()
    dispatch = mocker.spy(routes.outbox, "dispatch")

    tasks.delete_account(user_id=user.pk)

    dispatch.assert_called_once_with(
        {"type": "Delete", "object": {"type": actor.type}}, context={"actor": actor}
    )

    with pytest.raises(user.DoesNotExist):
        user.refresh_from_db()

    with pytest.raises(library.DoesNotExist):
        library.refresh_from_db()

    # this one shouldn't be deleted
    unrelated_library.refresh_from_db()
    actor.refresh_from_db()

    assert actor.type == "Tombstone"
    assert actor.name is None
    assert actor.summary is None
    # this activity shouldn't be deleted
    assert actor.outbox_activities.filter(type="Delete").count() == 1
