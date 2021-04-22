# Generated by Django 3.1.7 on 2021-04-21 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veche', '0004_auto_20210417_0043'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='community',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='communityrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='requestresolution',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания'),
        ),
    ]
