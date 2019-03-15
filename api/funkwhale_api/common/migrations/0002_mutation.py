# Generated by Django 2.1.5 on 2019-01-31 15:44

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("federation", "0017_auto_20190130_0926"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mutation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fid", models.URLField(db_index=True, max_length=500, unique=True)),
                (
                    "uuid",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                ("type", models.CharField(db_index=True, max_length=100)),
                ("is_approved", models.NullBooleanField(default=None)),
                ("is_applied", models.NullBooleanField(default=None)),
                (
                    "creation_date",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "applied_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("summary", models.TextField(max_length=2000, blank=True, null=True)),
                ("payload", django.contrib.postgres.fields.jsonb.JSONField()),
                (
                    "previous_state",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        null=True, default=None
                    ),
                ),
                ("target_id", models.IntegerField(null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_mutations",
                        to="federation.Actor",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_mutations",
                        to="federation.Actor",
                    ),
                ),
                (
                    "target_content_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="targeting_mutations",
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
        )
    ]