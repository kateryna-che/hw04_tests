# Generated by Django 2.2.16 on 2022-08-11 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220811_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(verbose_name='Дата публикации'),
        ),
    ]