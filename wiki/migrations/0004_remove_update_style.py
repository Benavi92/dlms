# Generated by Django 2.2 on 2020-04-06 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_update_style'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='update',
            name='style',
        ),
    ]