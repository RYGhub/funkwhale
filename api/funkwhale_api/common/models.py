import uuid

from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections, models, transaction
from django.db.models import Lookup
from django.db.models.fields import Field
from django.db.models.sql.compiler import SQLCompiler
from django.utils import timezone
from django.urls import reverse

from funkwhale_api.federation import utils as federation_utils


@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = "ne"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s <> %s" % (lhs, rhs), params


class NullsLastSQLCompiler(SQLCompiler):
    def get_order_by(self):
        result = super().get_order_by()
        if result and self.connection.vendor == "postgresql":
            return [
                (
                    expr,
                    (
                        sql + " NULLS LAST" if not sql.endswith(" NULLS LAST") else sql,
                        params,
                        is_ref,
                    ),
                )
                for (expr, (sql, params, is_ref)) in result
            ]
        return result


class NullsLastQuery(models.sql.query.Query):
    """Use a custom compiler to inject 'NULLS LAST' (for PostgreSQL)."""

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return NullsLastSQLCompiler(self, connection, using)


class NullsLastQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or NullsLastQuery(self.model)


class LocalFromFidQuerySet:
    def local(self, include=True):
        host = settings.FEDERATION_HOSTNAME
        query = models.Q(fid__startswith="http://{}/".format(host)) | models.Q(
            fid__startswith="https://{}/".format(host)
        )
        if include:
            return self.filter(query)
        else:
            return self.filter(~query)


class MutationQuerySet(models.QuerySet):
    def get_for_target(self, target):
        content_type = ContentType.objects.get_for_model(target)
        return self.filter(target_content_type=content_type, target_id=target.pk)


class Mutation(models.Model):
    fid = models.URLField(unique=True, max_length=500, db_index=True)
    uuid = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4)
    created_by = models.ForeignKey(
        "federation.Actor",
        related_name="created_mutations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        "federation.Actor",
        related_name="approved_mutations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    type = models.CharField(max_length=100, db_index=True)
    # None = no choice, True = approved, False = refused
    is_approved = models.NullBooleanField(default=None)

    # None = not applied, True = applied, False = failed
    is_applied = models.NullBooleanField(default=None)
    creation_date = models.DateTimeField(default=timezone.now, db_index=True)
    applied_date = models.DateTimeField(null=True, blank=True, db_index=True)
    summary = models.TextField(max_length=2000, null=True, blank=True)

    payload = JSONField(encoder=DjangoJSONEncoder)
    previous_state = JSONField(null=True, default=None, encoder=DjangoJSONEncoder)

    target_id = models.IntegerField(null=True)
    target_content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE,
        related_name="targeting_mutations",
    )
    target = GenericForeignKey("target_content_type", "target_id")

    objects = MutationQuerySet.as_manager()

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse("federation:edits-detail", kwargs={"uuid": self.uuid})
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid:
            self.fid = self.get_federation_id()

        return super().save(**kwargs)

    @transaction.atomic
    def apply(self):
        from . import mutations

        if self.is_applied:
            raise ValueError("Mutation was already applied")

        previous_state = mutations.registry.apply(
            type=self.type, obj=self.target, payload=self.payload
        )
        self.previous_state = previous_state
        self.is_applied = True
        self.applied_date = timezone.now()
        self.save(update_fields=["is_applied", "applied_date", "previous_state"])
        return previous_state
