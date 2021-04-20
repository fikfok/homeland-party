from django.db import models
from django.contrib.auth.models import User

from homeland_party.const import DEFAULT_LAT, DEFAULT_LON
from personal_cabinet.mixins.geo_mixin import GeoMixin
from veche.models import Community, CommunityRequest, RequestResolution


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
        user_has_not_geo_community_request = self.user_has_not_geo_community_request()
        return geo_exists and username_exists and user_has_not_geo_community_request

    def user_can_create_geo_community(self) -> bool:
        geo_exists = bool(self.get_geo())
        user_not_in_geo_community = not self.user_in_geo_community()
        user_has_not_geo_community_request = self.user_has_not_geo_community_request()
        username_exists = bool(self.user.username)

        user_can_create_geo_community = False
        if geo_exists and user_not_in_geo_community and username_exists and user_has_not_geo_community_request:
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
        # TODO Но по сути тут никак не определяется гео это десятка или не не гео.
        open_status = CommunityRequest.REQUEST_STATUS_OPEN_KEY
        ten_type = Community.COMMUNITY_TYPE_TEN_KEY
        result = not CommunityRequest.objects. \
            filter(author=self.user, status=open_status, community__type=ten_type). \
            exists()
        return result

    def get_created_by_me_community_request(self) -> CommunityRequest:
        open_status = CommunityRequest.REQUEST_STATUS_OPEN_KEY
        return CommunityRequest.objects.filter(author=self.user, status=open_status).first()

    def did_user_create_community_request(self) -> bool:
        return bool(self.get_created_by_me_community_request())

    def get_requests_user_need_to_approve(self) -> list:
        open_status = CommunityRequest.REQUEST_STATUS_OPEN_KEY
        ten_type = Community.COMMUNITY_TYPE_TEN_KEY
        geo_communities_qs = self.geo_community.all().filter(type=ten_type)
        result = []
        for geo_community in geo_communities_qs:
            requests = geo_community. \
                community_requests. \
                all(). \
                filter(status=open_status). \
                all()
            result += list(requests)
        return result

    def does_user_have_to_approve_requests(self) -> bool:
        return bool(self.get_requests_user_need_to_approve())

    def is_it_my_request(self, some_request) -> bool:
        requests = self.get_requests_user_need_to_approve()
        result = False
        for request in requests:
            if some_request.pk == request.pk:
                result = True
                break
        return result

    def did_user_resolve_request(self, community_request) -> bool:
        resolution_exists = RequestResolution.objects. \
            filter(community_request=community_request, author=self.user). \
            exists()
        return resolution_exists
