# Generated by Django 3.1.7 on 2021-03-31 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('personal_cabinet', '0011_auto_20210331_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geo',
            name='profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='geo', to='personal_cabinet.profile'),
        ),
    ]
