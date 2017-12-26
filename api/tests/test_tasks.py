import pytest

from funkwhale_api.taskapp import celery


class Dummy:
    @staticmethod
    def noop(instance):
        pass


def test_require_instance_decorator(factories, mocker):
    user = factories['users.User']()

    @celery.require_instance(user.__class__, 'user')
    def t(user):
        Dummy.noop(user)

    m = mocker.patch.object(Dummy, 'noop')
    t(user_id=user.pk)

    m.assert_called_once_with(user)


def test_require_instance_decorator_accepts_qs(factories, mocker):
    user = factories['users.User'](is_active=False)
    qs = user.__class__.objects.filter(is_active=True)

    @celery.require_instance(qs, 'user')
    def t(user):
        pass
    with pytest.raises(user.__class__.DoesNotExist):
        t(user_id=user.pk)
