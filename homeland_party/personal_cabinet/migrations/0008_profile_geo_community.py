# Generated by Django 3.1.7 on 2021-03-31 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('veche', '0001_initial'),
        ('personal_cabinet', '0007_auto_20210325_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='geo_community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='geo_community', to='veche.community'),
        ),
    ]
