# Generated by Django 3.1.7 on 2021-03-19 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_cabinet', '0003_custom_create_profiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='max_invites',
            field=models.IntegerField(default=5, verbose_name='Максимальное количество приглашений'),
        ),
    ]
