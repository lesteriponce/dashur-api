from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(default='en', max_length=10, verbose_name='Language')),
                ('timezone', models.CharField(default='UTC', max_length=50, verbose_name='Timezone')),
                ('email_notifications', models.BooleanField(default=True, verbose_name='Email Notifications')),
                ('push_notifications', models.BooleanField(default=True, verbose_name='Push Notifications')),
                ('marketing_emails', models.BooleanField(default=False, verbose_name='Marketing Emails')),
                ('theme', models.CharField(default='light', max_length=20, verbose_name='Theme')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Preference',
                'verbose_name_plural': 'User Preferences',
                'db_table': 'user_preferences',
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40, unique=True, verbose_name='Session Key')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP Address')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('last_activity', models.DateTimeField(auto_now=True, verbose_name='Last Activity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Session',
                'verbose_name_plural': 'User Sessions',
                'db_table': 'user_sessions',
                'ordering': ['-last_activity'],
                'indexes': [models.Index(fields=['user', 'is_active'], name='user_sessio_user_id_bb1b83_idx'), models.Index(fields=['session_key'], name='user_sessio_session_cc84b9_idx'), models.Index(fields=['last_activity'], name='user_sessio_last_ac_7cb421_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100, verbose_name='Action')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='User Agent')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Activity',
                'verbose_name_plural': 'User Activities',
                'db_table': 'user_activities',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['user', 'timestamp'], name='user_activi_user_id_d06d90_idx'), models.Index(fields=['action'], name='user_activi_action_b4118c_idx'), models.Index(fields=['timestamp'], name='user_activi_timesta_12eff7_idx')],
            },
        ),
    ]
