import logging
from django.core import mail
from django.conf import settings
from django.db import transaction
from django.dispatch import receiver

from funkwhale_api.common import channels
from funkwhale_api.common import preferences
from funkwhale_api.common import utils
from funkwhale_api.taskapp import celery
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.users import models as users_models

from . import models
from . import signals

logger = logging.getLogger(__name__)


@receiver(signals.report_created)
def broadcast_report_created(report, **kwargs):
    from . import serializers

    channels.group_send(
        "admin.moderation",
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "report.created",
                "report": serializers.ReportSerializer(report).data,
                "unresolved_count": models.Report.objects.filter(
                    is_handled=False
                ).count(),
            },
        },
    )


@receiver(signals.report_created)
def trigger_moderator_email(report, **kwargs):
    if settings.MODERATION_EMAIL_NOTIFICATIONS_ENABLED:
        utils.on_commit(send_new_report_email_to_moderators.delay, report_id=report.pk)


def get_moderators():
    moderators = users_models.User.objects.filter(
        is_active=True, permission_moderation=True
    )
    if not moderators:
        # we fallback on superusers
        moderators = users_models.User.objects.filter(is_superuser=True)
    moderators = sorted(moderators, key=lambda m: m.pk)
    return moderators


@celery.app.task(name="moderation.send_new_report_email_to_moderators")
@celery.require_instance(
    models.Report.objects.select_related("submitter").filter(is_handled=False), "report"
)
def send_new_report_email_to_moderators(report):
    moderators = get_moderators()
    submitter_repr = (
        report.submitter.full_username if report.submitter else report.submitter_email
    )
    subject = "[{} moderation - {}] New report from {}".format(
        settings.FUNKWHALE_HOSTNAME, report.get_type_display(), submitter_repr
    )
    detail_url = federation_utils.full_url(
        "/manage/moderation/reports/{}".format(report.uuid)
    )
    unresolved_reports_url = federation_utils.full_url(
        "/manage/moderation/reports?q=resolved:no"
    )
    unresolved_reports = models.Report.objects.filter(is_handled=False).count()
    body = [
        '{} just submitted a report in the "{}" category.'.format(
            submitter_repr, report.get_type_display()
        ),
        "",
        "Reported object: {} - {}".format(
            report.target._meta.verbose_name.title(), str(report.target)
        ),
    ]
    if hasattr(report.target, "get_absolute_url"):
        body.append(
            "Open public page: {}".format(
                federation_utils.full_url(report.target.get_absolute_url())
            )
        )
    if hasattr(report.target, "get_moderation_url"):
        body.append(
            "Open moderation page: {}".format(
                federation_utils.full_url(report.target.get_moderation_url())
            )
        )
    if report.summary:
        body += ["", "Report content:", "", report.summary]

    body += [
        "",
        "- To handle this report, please visit {}".format(detail_url),
        "- To view all unresolved reports (currently {}), please visit {}".format(
            unresolved_reports, unresolved_reports_url
        ),
        "",
        "—",
        "",
        "You are receiving this email because you are a moderator for {}.".format(
            settings.FUNKWHALE_HOSTNAME
        ),
    ]

    for moderator in moderators:
        if not moderator.email:
            logger.warning("Moderator %s has no email configured", moderator.username)
            continue
        mail.send_mail(
            subject,
            message="\n".join(body),
            recipient_list=[moderator.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )


@celery.app.task(name="moderation.user_request_handle")
@celery.require_instance(
    models.UserRequest.objects.select_related("submitter"), "user_request"
)
@transaction.atomic
def user_request_handle(user_request, new_status, old_status=None):
    if user_request.status != new_status:
        logger.warn(
            "User request %s was handled before asynchronous tasks run", user_request.pk
        )
        return

    if user_request.type == "signup" and new_status == "pending" and old_status is None:
        notify_mods_signup_request_pending(user_request)
        broadcast_user_request_created(user_request)
    elif user_request.type == "signup" and new_status == "approved":
        user_request.submitter.user.is_active = True
        user_request.submitter.user.save(update_fields=["is_active"])
        notify_submitter_signup_request_approved(user_request)
    elif user_request.type == "signup" and new_status == "refused":
        notify_submitter_signup_request_refused(user_request)


def broadcast_user_request_created(user_request):
    from funkwhale_api.manage import serializers as manage_serializers

    channels.group_send(
        "admin.moderation",
        {
            "type": "event.send",
            "text": "",
            "data": {
                "type": "user_request.created",
                "user_request": manage_serializers.ManageUserRequestSerializer(
                    user_request
                ).data,
                "pending_count": models.UserRequest.objects.filter(
                    status="pending"
                ).count(),
            },
        },
    )


def notify_mods_signup_request_pending(obj):
    moderators = get_moderators()
    submitter_repr = obj.submitter.preferred_username
    subject = "[{} moderation] New sign-up request from {}".format(
        settings.FUNKWHALE_HOSTNAME, submitter_repr
    )
    detail_url = federation_utils.full_url(
        "/manage/moderation/requests/{}".format(obj.uuid)
    )
    unresolved_requests_url = federation_utils.full_url(
        "/manage/moderation/requests?q=status:pending"
    )
    unresolved_requests = models.UserRequest.objects.filter(status="pending").count()
    body = [
        "{} wants to register on your pod. You need to review their request before they can use the service.".format(
            submitter_repr
        ),
        "",
        "- To handle this request, please visit {}".format(detail_url),
        "- To view all unresolved requests (currently {}), please visit {}".format(
            unresolved_requests, unresolved_requests_url
        ),
        "",
        "—",
        "",
        "You are receiving this email because you are a moderator for {}.".format(
            settings.FUNKWHALE_HOSTNAME
        ),
    ]

    for moderator in moderators:
        if not moderator.email:
            logger.warning("Moderator %s has no email configured", moderator.username)
            continue
        mail.send_mail(
            subject,
            message="\n".join(body),
            recipient_list=[moderator.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )


def notify_submitter_signup_request_approved(user_request):
    submitter_repr = user_request.submitter.preferred_username
    submitter_email = user_request.submitter.user.email
    if not submitter_email:
        logger.warning("User %s has no email configured", submitter_repr)
        return
    subject = "Welcome to {}, {}!".format(settings.FUNKWHALE_HOSTNAME, submitter_repr)
    login_url = federation_utils.full_url("/login")
    body = [
        "Hi {} and welcome,".format(submitter_repr),
        "",
        "Our moderation team has approved your account request and you can now start "
        "using the service. Please visit {} to get started.".format(login_url),
        "",
        "Before your first login, you may need to verify your email address if you didn't already.",
    ]

    mail.send_mail(
        subject,
        message="\n".join(body),
        recipient_list=[submitter_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )


def notify_submitter_signup_request_refused(user_request):
    submitter_repr = user_request.submitter.preferred_username
    submitter_email = user_request.submitter.user.email
    if not submitter_email:
        logger.warning("User %s has no email configured", submitter_repr)
        return
    subject = "Your account request at {} was refused".format(
        settings.FUNKWHALE_HOSTNAME
    )
    body = [
        "Hi {},".format(submitter_repr),
        "",
        "You recently submitted an account request on our service. However, our "
        "moderation team has refused it, and as a result, you won't be able to use "
        "the service.",
    ]

    instance_contact_email = preferences.get("instance__contact_email")
    if instance_contact_email:
        body += [
            "",
            "If you think this is a mistake, please contact our team at {}.".format(
                instance_contact_email
            ),
        ]

    mail.send_mail(
        subject,
        message="\n".join(body),
        recipient_list=[submitter_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
    )
