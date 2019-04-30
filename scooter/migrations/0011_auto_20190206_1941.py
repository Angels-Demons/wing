# Generated by Django 2.1.1 on 2019-02-06 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scooter', '0010_auto_20190206_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='distance',
            field=models.SmallIntegerField(null=True, verbose_name='distance(km)'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='duration',
            field=models.FloatField(null=True, verbose_name='duration(m)'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='end_point_latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True, verbose_name='end Lat'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='end_point_longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True, verbose_name='end Lng'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='start_point_latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, verbose_name='start Lat'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='start_point_longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, verbose_name='start Lng'),
        ),
    ]