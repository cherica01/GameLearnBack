# Generated by Django 5.1.7 on 2025-04-05 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chathistory',
            name='character',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
