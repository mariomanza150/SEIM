# Generated manually for profile implementation completion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0008_userprofile_student_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="academic_level",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Not Specified"),
                    ("UNDERGRADUATE", "Undergraduate"),
                    ("GRADUATE", "Graduate"),
                    ("DOCTORAL", "Doctoral"),
                    ("POSTDOC", "Post-Doctoral"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="email_notifications",
            field=models.BooleanField(
                default=True, help_text="Receive email notifications"
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="field_of_study",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="gpa",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="GPA on 4.0 scale",
                max_digits=3,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="graduation_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="interface_language",
            field=models.CharField(blank=True, default="en", max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="marketing_emails",
            field=models.BooleanField(
                default=False, help_text="Receive marketing communications"
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="skills",
            field=models.TextField(
                blank=True, help_text="List your skills, separated by commas", null=True
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="sms_notifications",
            field=models.BooleanField(
                default=False, help_text="Receive SMS notifications"
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="timezone",
            field=models.CharField(blank=True, default="UTC", max_length=50, null=True),
        ),
    ]
