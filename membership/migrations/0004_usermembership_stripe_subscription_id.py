# Generated by Django 4.0.1 on 2022-02-01 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0003_usermembership_end_date_usermembership_start_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermembership',
            name='stripe_subscription_id',
            field=models.CharField(default='', max_length=255),
        ),
    ]
