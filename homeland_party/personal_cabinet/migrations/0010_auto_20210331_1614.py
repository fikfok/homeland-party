# Generated by Django 3.1.7 on 2021-03-31 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('personal_cabinet', '0009_auto_20210331_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='geo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='geo', to='personal_cabinet.geo'),
        ),
    ]
