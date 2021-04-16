from django.db import models
from django.contrib.auth.models import User

from homeland_party.const import DEFAULT_LAT, DEFAULT_LON
from personal_cabinet.mixins.geo_mixin import GeoMixin
from veche.models import Community, CommunityRequest


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

    def user_can_join_in_geo_community(self):
        geo_exists = bool(self.get_geo())
        username_exists = bool(self.user.username)
        return geo_exists and username_exists

    def user_can_create_geo_community(self) -> bool:
        geo_exists = bool(self.get_geo())
        user_not_in_geo_community = not self.user_in_geo_community()
        user_can_create_geo_community = False
        username_exists = bool(self.user.username)
        if geo_exists and user_not_in_geo_community and username_exists:
            user_can_create_geo_community = True
        return user_can_create_geo_community

    def user_in_geo_community(self) -> bool:
        return self.geo_community.all().exists()

    def get_form_data(self) -> dict:
        geo = self.get_geo()
        data = {
            'user_name': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'latitude': geo.geo_lat if geo else DEFAULT_LAT,
            'longitude': geo.geo_lon if geo else DEFAULT_LON,
            'birth_date': self.birth_date.strftime("%d.%m.%Y") if self.birth_date else None
        }
        return data

    def get_card_data(self) -> dict:
        geo = self.get_geo()
        data = self.get_form_data()
        data['address'] = str(geo) if geo else ''
        return data

    def user_has_not_geo_community_request(self) -> bool:
        open_status = CommunityRequest.REQUEST_STATUS_OPEN_KEY
        return not CommunityRequest.objects.filter(author=self.user, status=open_status).exists()
