# Generated by Django 2.1.1 on 2019-02-03 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charging', '0002_auto_20190203_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='tariff',
            name='per_kilometer_price',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]