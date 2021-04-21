# Generated by Django 3.1.7 on 2021-04-16 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('veche', '0002_communityrequest_requestresolution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestresolution',
            name='community_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resolutions', to='veche.communityrequest'),
        ),
    ]