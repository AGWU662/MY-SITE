from django.db import migrations, models


def update_existing_min_deposit(apps, schema_editor):
    """Update any existing SiteSettings rows that still have the old default of 100."""
    SiteSettings = apps.get_model('accounts', 'SiteSettings')
    SiteSettings.objects.filter(min_deposit=100).update(min_deposit=30)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_remove_tawk_add_smartsupp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='min_deposit',
            field=models.DecimalField(decimal_places=2, default=30, max_digits=15),
        ),
        migrations.RunPython(update_existing_min_deposit, migrations.RunPython.noop),
    ]
