from django.db import models
from django.contrib.auth.models import User


class Geo(models.Model):
    class Meta:
        verbose_name = 'Гео'
        verbose_name_plural = 'Гео'

    label = models.CharField(verbose_name='Название географии', max_length=1000)
    parent = models.ForeignKey('self', verbose_name='Родительская география', blank=True, null=True,
                               related_name='children', on_delete=models.CASCADE)
    lon = models.FloatField(verbose_name='Долгота', null=True, blank=True)
    lat = models.FloatField(verbose_name='Широта', null=True, blank=True)

    def __str__(self):
        return self.label


class Profile(models.Model):
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    MAX_INVITES_DEFAULT = 5
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    geo = models.ForeignKey(Geo, related_name='geo', on_delete=models.CASCADE, null=True, blank=True)
    max_invites = models.IntegerField(verbose_name='Максимальное количество приглашений', default=MAX_INVITES_DEFAULT)

    def __str__(self):
        return self.user.email
