# Generated by Django 3.1.7 on 2021-03-24 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_cabinet', '0006_auto_20210324_2356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geo',
            name='federal_district',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Федеральный округ'),
        ),
    ]
