# Generated by Django 3.2.3 on 2021-05-16 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20210516_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='markers',
            name='lat',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='markers',
            name='lng',
            field=models.IntegerField(default=0),
        ),
    ]
