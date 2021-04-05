from django.contrib.auth.models import User
from django.db import migrations, models

from personal_cabinet.models.models import Profile


def create_profiles(apps, schema_editor):
    for user in User.objects.all():
        Profile.objects.create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('personal_cabinet', '0002_auto_20210319_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='geo',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE,
                                    related_name='geo', to='personal_cabinet.geo'),
        ),
        migrations.RunPython(create_profiles, reverse_code=migrations.RunPython.noop),
    ]
