# Generated by Django 4.2.2 on 2023-12-15 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    replaces = [
        ("fedcode", "0001_initial"),
        ("fedcode", "0002_alter_reputation_unique_together"),
        ("fedcode", "0003_alter_person_summary_alter_purl_notes_and_more"),
        ("fedcode", "0004_alter_review_remote_url"),
    ]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RemoteActor",
            fields=[
                ("url", models.URLField(primary_key=True, serialize=False)),
                ("username", models.CharField(max_length=100)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The object's unique global identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("acct", models.CharField(max_length=200)),
                ("content", models.TextField()),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="A field to track when notes are created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="A field to track when notes are updated"
                    ),
                ),
                (
                    "reply_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to="fedcode.note",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("summary", models.CharField(help_text="profile summary", max_length=100)),
                ("public_key", models.TextField()),
                ("local", models.BooleanField(default=True)),
                (
                    "avatar",
                    models.ImageField(default="favicon-16x16.png", null=True, upload_to="uploads/"),
                ),
                ("notes", models.ManyToManyField(blank=True, to="fedcode.note")),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "remote_actor",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fedcode.remoteactor",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Purl",
            fields=[
                ("summary", models.CharField(max_length=100)),
                ("public_key", models.TextField()),
                ("local", models.BooleanField(default=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The object's unique global identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "string",
                    models.CharField(
                        help_text="PURL (no version) ex: @pkg:maven/org.apache.logging",
                        max_length=300,
                    ),
                ),
                ("notes", models.ManyToManyField(blank=True, to="fedcode.note")),
                (
                    "remote_actor",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fedcode.remoteactor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fedcode.person"
                    ),
                ),
                (
                    "purl",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fedcode.purl"
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Reputation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("voter", models.CharField(help_text="security@vcio.com", max_length=100)),
                ("acceptor", models.CharField(help_text="security@nexb.com", max_length=100)),
                ("positive", models.BooleanField(default=True)),
            ],
            options={
                "unique_together": {("voter", "acceptor")},
            },
        ),
        migrations.AddField(
            model_name="note",
            name="reputation",
            field=models.ManyToManyField(blank=True, to="fedcode.reputation"),
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "remote_actor",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fedcode.remoteactor",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Repository",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The object's unique global identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(help_text="repository name", max_length=50)),
                (
                    "url",
                    models.URLField(
                        help_text="repository url ex: https://github.com/nexB/federatedcode"
                    ),
                ),
                ("path", models.CharField(help_text="path of the repository", max_length=200)),
                (
                    "remote_url",
                    models.CharField(
                        blank=True,
                        help_text="the url of the repository if this repository is remote",
                        max_length=300,
                        null=True,
                    ),
                ),
                ("last_imported_commit", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "admin",
                    models.ForeignKey(
                        help_text="admin user ex: VCIO user",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fedcode.service",
                    ),
                ),
            ],
            options={
                "unique_together": {("admin", "name")},
            },
        ),
        migrations.AddField(
            model_name="purl",
            name="service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="fedcode.service",
            ),
        ),
        migrations.CreateModel(
            name="Vulnerability",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The object's unique global identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("filename", models.CharField(max_length=255)),
                ("remote_url", models.CharField(blank=True, max_length=300, null=True)),
                (
                    "repo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fedcode.repository"
                    ),
                ),
            ],
            options={
                "unique_together": {("repo", "filename")},
            },
        ),
        migrations.AlterUniqueTogether(
            name="purl",
            unique_together={("service", "remote_actor", "string")},
        ),
        migrations.AlterField(
            model_name="purl",
            name="notes",
            field=models.ManyToManyField(
                blank=True,
                help_text="the notes that this purl created ex:\n                                                               purl: pkg:.../.../\n                                                               affected_by_vulnerabilities: []\n                                                               fixing_vulnerabilities: []\n                                                               ",
                to="fedcode.note",
            ),
        ),
        migrations.AlterField(
            model_name="purl",
            name="summary",
            field=models.CharField(help_text="profile summary", max_length=100),
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="The object's unique global identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("headline", models.CharField(help_text="the review title", max_length=300)),
                ("commit_id", models.CharField(max_length=300)),
                ("data", models.TextField(help_text="review data ex: vulnerability file")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="A field to track when review are created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="A field to track when review are updated"
                    ),
                ),
                (
                    "remote_url",
                    models.CharField(
                        blank=True,
                        help_text="the review remote url if Remote Review exists",
                        max_length=300,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Open"), (1, "Draft"), (2, "Closed"), (3, "Merged")],
                        default=0,
                        help_text="status of review",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fedcode.person"
                    ),
                ),
                ("notes", models.ManyToManyField(blank=True, to="fedcode.note")),
                ("reputation", models.ManyToManyField(blank=True, to="fedcode.reputation")),
                (
                    "vulnerability",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fedcode.vulnerability"
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
    ]