# Generated by Django 3.1.7 on 2021-04-02 21:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('personal_cabinet', '0014_auto_20210401_1913'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geo',
            name='profile',
        ),
        migrations.AddField(
            model_name='geo',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='ID сущности'),
        ),
        migrations.AddField(
            model_name='geo',
            name='object_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='related_object_type', to='contenttypes.contenttype', verbose_name='Тип сущности'),
        ),
    ]
