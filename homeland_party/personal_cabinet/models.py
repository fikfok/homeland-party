from django.db import models
from django.contrib.auth.models import User

from personal_cabinet.geo_mixin import GeoMixin
from veche.models import Community


class Profile(GeoMixin, models.Model):
    MAX_INVITES_DEFAULT = 5

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    max_invites = models.IntegerField(verbose_name='Максимальное количество приглашений', default=MAX_INVITES_DEFAULT)
    geo_community = models.ManyToManyField(to=Community, related_name='geo_community', null=True, blank=True)

    def __str__(self):
        return f'{self.user.email}'

    def user_can_create_community(self) -> bool:
        user_not_in_geo_community = not self.user_in_geo_community()
        user_can_create_community = False
        if self.geo_exists() and user_not_in_geo_community:
            user_can_create_community = True
        return user_can_create_community

    def user_in_geo_community(self) -> bool:
        return self.geo_community.all().exists()
