# Generated by Django 3.1.7 on 2021-05-31 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('veche', '0010_initiative_involved_communities'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='initiative',
            options={'verbose_name': 'Инициатива', 'verbose_name_plural': 'Инициативы'},
        ),
        migrations.AlterModelOptions(
            name='messageinitiative',
            options={'verbose_name': 'Сообщения инициативы', 'verbose_name_plural': 'Сообщения инициатив'},
        ),
    ]
