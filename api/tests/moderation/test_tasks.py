from funkwhale_api.federation import utils as federation_utils

from funkwhale_api.moderation import tasks


def test_report_created_signal_calls_send_new_report_mail(factories, mocker):
    report = factories["moderation.Report"]()
    on_commit = mocker.patch("funkwhale_api.common.utils.on_commit")
    tasks.signals.report_created.send(sender=None, report=report)
    on_commit.assert_called_once_with(
        tasks.send_new_report_email_to_moderators.delay, report_id=report.pk
    )


def test_report_created_signal_sends_email_to_mods(factories, mailoutbox, settings):
    mod1 = factories["users.User"](permission_moderation=True)
    mod2 = factories["users.User"](permission_moderation=True)
    # inactive, so no email
    factories["users.User"](permission_moderation=True, is_active=False)
    # no moderation permission, so no email
    factories["users.User"]()

    report = factories["moderation.Report"]()

    tasks.send_new_report_email_to_moderators(report_id=report.pk)

    detail_url = federation_utils.full_url(
        "/manage/moderation/reports/{}".format(report.uuid)
    )
    unresolved_reports_url = federation_utils.full_url(
        "/manage/moderation/reports?q=resolved:no"
    )
    assert len(mailoutbox) == 2
    for i, mod in enumerate([mod1, mod2]):
        m = mailoutbox[i]
        assert m.subject == "[{} moderation - {}] New report from {}".format(
            settings.FUNKWHALE_HOSTNAME,
            report.get_type_display(),
            report.submitter.full_username,
        )
        assert report.summary in m.body
        assert report.target._meta.verbose_name.title() in m.body
        assert str(report.target) in m.body
        assert report.target.get_absolute_url() in m.body
        assert report.target.get_moderation_url() in m.body
        assert detail_url in m.body
        assert unresolved_reports_url in m.body
        assert list(m.to) == [mod.email]


def test_signup_request_pending_sends_email_to_mods(factories, mailoutbox, settings):
    mod1 = factories["users.User"](permission_moderation=True)
    mod2 = factories["users.User"](permission_moderation=True)

    signup_request = factories["moderation.UserRequest"](signup=True)

    tasks.user_request_handle(user_request_id=signup_request.pk, new_status="pending")

    detail_url = federation_utils.full_url(
        "/manage/moderation/requests/{}".format(signup_request.uuid)
    )
    unresolved_requests_url = federation_utils.full_url(
        "/manage/moderation/requests?q=status:pending"
    )
    assert len(mailoutbox) == 2
    for i, mod in enumerate([mod1, mod2]):
        m = mailoutbox[i]
        assert m.subject == "[{} moderation] New sign-up request from {}".format(
            settings.FUNKWHALE_HOSTNAME, signup_request.submitter.preferred_username,
        )
        assert detail_url in m.body
        assert unresolved_requests_url in m.body
        assert list(m.to) == [mod.email]


def test_approved_request_sends_email_to_submitter_and_set_active(
    factories, mailoutbox, settings
):
    user = factories["users.User"](is_active=False)
    actor = user.create_actor()
    signup_request = factories["moderation.UserRequest"](
        signup=True, submitter=actor, status="approved"
    )

    tasks.user_request_handle(user_request_id=signup_request.pk, new_status="approved")

    user.refresh_from_db()

    assert user.is_active is True
    assert len(mailoutbox) == 1
    m = mailoutbox[-1]
    login_url = federation_utils.full_url("/login")
    assert m.subject == "Welcome to {}, {}!".format(
        settings.FUNKWHALE_HOSTNAME, signup_request.submitter.preferred_username,
    )
    assert login_url in m.body
    assert list(m.to) == [user.email]


def test_refused_request_sends_email_to_submitter(
    factories, mailoutbox, settings, preferences
):
    preferences["instance__contact_email"] = "test@pod.example"
    user = factories["users.User"](is_active=False)
    actor = user.create_actor()
    signup_request = factories["moderation.UserRequest"](
        signup=True, submitter=actor, status="refused"
    )

    tasks.user_request_handle(user_request_id=signup_request.pk, new_status="refused")

    user.refresh_from_db()

    assert user.is_active is False

    assert len(mailoutbox) == 1
    m = mailoutbox[-1]
    assert m.subject == "Your account request at {} was refused".format(
        settings.FUNKWHALE_HOSTNAME,
    )
    assert "test@pod.example" in m.body
    assert list(m.to) == [user.email]
