from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_add_chat_transcript_event_type'),
    ]

    operations = [
        # Drop the TawkChatLog table
        migrations.DeleteModel(
            name='TawkChatLog',
        ),
        # Remove old tawk_property_id field from SiteSettings
        migrations.RemoveField(
            model_name='sitesettings',
            name='tawk_property_id',
        ),
        # Add new smartsupp_api_key field to SiteSettings
        migrations.AddField(
            model_name='sitesettings',
            name='smartsupp_api_key',
            field=models.CharField(blank=True, help_text='Smartsupp API Key', max_length=100),
        ),
    ]
