from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_user_managers_remove_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Admin email')),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='Username')),
                ('password', models.CharField(max_length=255, verbose_name='Password')),
                ('first_name', models.CharField(max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('is_super_admin', models.BooleanField(default=False, verbose_name='Super Admin')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='Last login')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Admin User',
                'verbose_name_plural': 'Admin Users',
                'db_table': 'admin_users',
                'ordering': ['-created_at'],
            },
        ),
    ]
