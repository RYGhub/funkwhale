import logging
from django.core import mail
from django.dispatch import receiver
from django.conf import settings

from funkwhale_api.common import channels
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


@celery.app.task(name="moderation.send_new_report_email_to_moderators")
@celery.require_instance(
    models.Report.objects.select_related("submitter").filter(is_handled=False), "report"
)
def send_new_report_email_to_moderators(report):
    moderators = users_models.User.objects.filter(
        is_active=True, permission_moderation=True
    )
    if not moderators:
        # we fallback on superusers
        moderators = users_models.User.objects.filter(is_superuser=True)
    moderators = sorted(moderators, key=lambda m: m.pk)
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
