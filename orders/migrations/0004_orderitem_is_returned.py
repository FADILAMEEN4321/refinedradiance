# Generated by Django 4.2.2 on 2023-07-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_returnitem_orderitem_return_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_returned',
            field=models.BooleanField(default=False),
        ),
    ]
