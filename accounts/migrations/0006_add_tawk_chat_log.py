# Generated migration for TawkChatLog model

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_site_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='TawkChatLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_type', models.CharField(choices=[('chat:start', 'Chat Started'), ('chat:end', 'Chat Ended'), ('ticket:create', 'Ticket Created')], max_length=50)),
                ('chat_id', models.CharField(blank=True, max_length=100)),
                ('visitor_name', models.CharField(blank=True, max_length=200)),
                ('visitor_email', models.CharField(blank=True, max_length=200)),
                ('visitor_city', models.CharField(blank=True, max_length=100)),
                ('visitor_country', models.CharField(blank=True, max_length=100)),
                ('message_preview', models.TextField(blank=True)),
                ('agent_name', models.CharField(blank=True, max_length=200)),
                ('raw_data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Tawk Chat Log',
                'verbose_name_plural': 'Tawk Chat Logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
