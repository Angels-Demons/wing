# Generated by Django 2.0.3 on 2018-11-15 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ride', '0003_auto_20181108_1626'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ride',
            old_name='rider',
            new_name='user',
        ),
    ]
