# Generated by Django 3.0.5 on 2020-05-26 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Publisher', '0005_channel_sended'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='name',
            field=models.CharField(default='ninguno', max_length=100),
        ),
        migrations.AddField(
            model_name='channel',
            name='token_secret',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]