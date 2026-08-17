# Generated manually for host-subject catalog relaxation + grade workflow.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def backfill_host_subject_institution(apps, schema_editor):
    HostSubject = apps.get_model("exchange", "HostSubject")
    for subject in HostSubject.objects.select_related(
        "academic_program__school"
    ).iterator():
        academic = subject.academic_program
        if academic is None:
            continue
        school = academic.school
        subject.school_id = school.id
        subject.institution_id = school.institution_id
        subject.save(update_fields=["school_id", "institution_id"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exchange", "0029_agreementcomment"),
        ("grades", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hostinstitution",
            name="grade_scale",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Host university grading scale used for subject grade dropdowns "
                    "and course-level translation."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="host_institutions",
                to="grades.gradescale",
            ),
        ),
        migrations.AddField(
            model_name="hostsubject",
            name="institution",
            field=models.ForeignKey(
                help_text="Host university this subject belongs to.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subjects",
                to="exchange.hostinstitution",
            ),
        ),
        migrations.AddField(
            model_name="hostsubject",
            name="school",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional faculty / school. Must belong to the institution.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subjects",
                to="exchange.hostschool",
            ),
        ),
        migrations.RunPython(backfill_host_subject_institution, noop_reverse),
        migrations.AlterField(
            model_name="hostsubject",
            name="institution",
            field=models.ForeignKey(
                help_text="Host university this subject belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subjects",
                to="exchange.hostinstitution",
            ),
        ),
        migrations.AlterField(
            model_name="hostsubject",
            name="academic_program",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional academic program. Must belong to the school.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subjects",
                to="exchange.hostacademicprogram",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="hostsubject",
            name="uniq_host_subject_program_name_code",
        ),
        migrations.AddConstraint(
            model_name="hostsubject",
            constraint=models.UniqueConstraint(
                fields=("institution", "name", "code"),
                name="uniq_host_subject_institution_name_code",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="applicationsubjectselection",
            name="uniq_application_host_subject_selection",
        ),
        migrations.AlterField(
            model_name="applicationsubjectselection",
            name="host_subject",
            field=models.ForeignKey(
                blank=True,
                help_text="Catalog host subject. Mutually exclusive with custom course fields.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="application_selections",
                to="exchange.hostsubject",
            ),
        ),
        migrations.AlterField(
            model_name="applicationsubjectselection",
            name="credits",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text=(
                    "Credits used for homologación (defaults to host subject or custom credits)."
                ),
                max_digits=5,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="custom_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Unlisted host course code (when not using the catalog).",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="custom_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Unlisted host course name (required when not using the catalog).",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="custom_credits",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Unlisted host course credits.",
                max_digits=5,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="proposed_host_grade",
            field=models.ForeignKey(
                blank=True,
                help_text="Host grade proposed by the student.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proposed_subject_selections",
                to="grades.gradevalue",
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="confirmed_host_grade",
            field=models.ForeignKey(
                blank=True,
                help_text="Host grade locked after coordinator confirmation.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="confirmed_subject_selections",
                to="grades.gradevalue",
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="home_grade",
            field=models.ForeignKey(
                blank=True,
                help_text="Translated home-scale grade written at confirmation.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="home_subject_selections",
                to="grades.gradevalue",
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="grade_status",
            field=models.CharField(
                choices=[
                    ("none", "None"),
                    ("proposed", "Proposed"),
                    ("confirmed", "Confirmed"),
                    ("rejected", "Rejected"),
                ],
                default="none",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="proposed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="proposed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proposed_subject_grades",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="confirmed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="confirmed_subject_grades",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="applicationsubjectselection",
            name="confirmation_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddConstraint(
            model_name="applicationsubjectselection",
            constraint=models.UniqueConstraint(
                condition=models.Q(("host_subject__isnull", False)),
                fields=("application", "host_subject"),
                name="uniq_application_host_subject_selection",
            ),
        ),
        migrations.AddConstraint(
            model_name="applicationsubjectselection",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        ("host_subject__isnull", False),
                        ("custom_name", ""),
                        ("custom_code", ""),
                        ("custom_credits__isnull", True),
                    )
                    | (
                        models.Q(("host_subject__isnull", True))
                        & ~models.Q(("custom_name", ""))
                    )
                ),
                name="application_subject_catalog_xor_custom",
            ),
        ),
    ]
