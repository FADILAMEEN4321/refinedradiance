# Generated by Django 4.2.2 on 2023-07-16 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_delete_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='wallet',
            field=models.FloatField(default=0),
        ),
    ]
