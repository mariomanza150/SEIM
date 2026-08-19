# UADEC catalog alignment: SchoolFaculty.unidad, Profile.toefl_score

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0019_alter_googlecalendarconnection_event_map"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="toefl_score",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="TOEFL score (paper-based or equivalent) for mobility eligibility.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="schoolfaculty",
            name="unidad",
            field=models.ForeignKey(
                blank=True,
                help_text="Campus unit this faculty belongs to (UAdeC Unidad Sureste/Laguna/Norte).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="school_faculties",
                to="accounts.unidad",
            ),
        ),
        migrations.AddConstraint(
            model_name="schoolfaculty",
            constraint=models.UniqueConstraint(
                fields=("unidad", "name"),
                name="accounts_schoolfaculty_unidad_name_uniq",
            ),
        ),
    ]
