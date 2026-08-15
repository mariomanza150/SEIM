"""Drop leftover tables from the removed unused ``plugins`` app.

``plugins`` shipped stub ``Plugin`` / ``PluginConfig`` models and
``0001_initial`` but was never used in production code. The app package is
gone; this migration cleans existing databases.

Fresh installs: ``DROP TABLE IF EXISTS`` is a no-op.
Existing installs: drops ``plugins_pluginconfig`` and ``plugins_plugin``,
then removes stale ``django_migrations`` rows for the uninstalled app.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_googlecalendarconnection_imported_events"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS plugins_pluginconfig CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS plugins_plugin CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DELETE FROM django_migrations WHERE app = 'plugins';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
