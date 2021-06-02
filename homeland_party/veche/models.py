from collections import namedtuple
from datetime import datetime, timedelta
from profile import Profile

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, F
from safedelete.models import SafeDeleteModel

from personal_cabinet.mixins.geo_mixin import GeoMixin


RequestStats = namedtuple('RequestStats', ('total_profiles', 'total_agreed', 'total_rejected'))


def initiative_default_expire_at() -> datetime:
    """
    Значение по-умолчанию даты истекания срока согласования инициативы
    :return: дата и время истечения срока годности приглашения
    """
    return datetime.now() + Initiative.APPROVAL_PERIOD_HOURS


class Community(GeoMixin, SafeDeleteModel, models.Model):
    COMMUNITY_TYPE_TEN_KEY = 'ten'
    COMMUNITY_TYPE_TEN_LABEL = 'десятка'

    COMMUNITY_TYPE_CHOICES = (
        (COMMUNITY_TYPE_TEN_KEY, COMMUNITY_TYPE_TEN_LABEL),
    )

    MAX_PARTICIPANTS = {
        COMMUNITY_TYPE_TEN_KEY: 10,
    }

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    type = models.CharField(verbose_name='Тип сообщества', choices=COMMUNITY_TYPE_CHOICES, max_length=50)
    max_participants = models.PositiveIntegerField(verbose_name='Максимальное количество дочерних элементов')

    @classmethod
    def get_geo_tens_for_join(cls):
        qs = Community.objects. \
            filter(type=Community.COMMUNITY_TYPE_TEN_KEY). \
            annotate(participants_count=Count('geo_community')). \
            filter(participants_count__lt=F('max_participants'))
        return qs

    def get_community_type_label(self):
        current_label = self.get_type_display().capitalize()
        return current_label

    def is_geo_ten_open(self):
        profiles_qs = self.get_profiles_qs()
        return self.max_participants > profiles_qs.count()

    def get_profiles_qs(self):
        from personal_cabinet.models.models import Profile

        return Profile.objects.filter(geo_community=self)

    @property
    def profiles_count(self):
        return self.get_profiles_qs().count()

    def is_geo_ten_complete(self):
        profiles_qs = self.get_profiles_qs()
        return self.max_participants == profiles_qs.count()

    def is_possible_to_create_initiative(self):
        return self.geo_exists() and self.is_geo_ten_complete()

    def get_initiatives(self):
        return self.community_initiatives.all()

    def __str__(self):
        geo = self.get_geo()
        current_label = self.get_community_type_label()
        return f'{current_label}. Адрес: {str(geo)}'


class CommunityRequest(SafeDeleteModel, models.Model):
    REQUEST_STATUS_OPEN_KEY = 'open'
    REQUEST_STATUS_OPEN_LABEL = 'открыта'
    REQUEST_STATUS_AGREED_KEY = 'agreed'
    REQUEST_STATUS_AGREED_LABEL = 'принята'
    REQUEST_STATUS_REJECTED_KEY = 'rejected'
    REQUEST_STATUS_REJECTED_LABEL = 'отклонена'

    STATUS_CHOICES = (
        (REQUEST_STATUS_OPEN_KEY, REQUEST_STATUS_OPEN_LABEL),
        (REQUEST_STATUS_AGREED_KEY, REQUEST_STATUS_AGREED_LABEL),
        (REQUEST_STATUS_REJECTED_KEY, REQUEST_STATUS_REJECTED_LABEL),
    )

    class Meta:
        verbose_name = 'Заявка на вступление в сообщество'
        verbose_name_plural = 'Заявки на вступление в сообщество'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    status = models.CharField(verbose_name='Статус заявки', choices=STATUS_CHOICES, max_length=20,
                              default=REQUEST_STATUS_OPEN_KEY)
    community = models.ForeignKey(to=Community, on_delete=models.CASCADE, related_name='community_requests')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True, db_index=True)

    def get_request_stats(self) -> RequestStats:
        total_profiles = self.community.get_profiles_qs().count()
        total_agreed = self.resolutions.filter(resolution=RequestResolution.RESOLUTION_AGREED_KEY).count()
        total_rejected = self.resolutions.filter(resolution=RequestResolution.RESOLUTION_REJECTED_KEY).count()
        stats = RequestStats(total_profiles=total_profiles, total_agreed=total_agreed, total_rejected=total_rejected)
        return stats

    @property
    def is_ok(self):
        return self.status == self.REQUEST_STATUS_AGREED_KEY

    @property
    def geo_comminuty(self):
        return self.community.get_geo()

    def did_all_participants_resolve(self) -> bool:
        stats = self.get_request_stats()
        return stats.total_profiles == stats.total_agreed + stats.total_rejected

    def does_request_have_reject(self) -> bool:
        stats = self.get_request_stats()
        return stats.total_rejected > 0

    def __str__(self):
        return f'Заявка от {self.author.username}. {self.community}'


class RequestResolution(SafeDeleteModel, models.Model):
    RESOLUTION_AGREED_KEY = 'agreed'
    RESOLUTION_AGREED_LABEL = 'принята'
    RESOLUTION_REJECTED_KEY = 'rejected'
    RESOLUTION_REJECTED_LABEL = 'отклонена'

    RESOLUTION_CHOICES = (
        (RESOLUTION_AGREED_KEY, RESOLUTION_AGREED_LABEL),
        (RESOLUTION_REJECTED_KEY, RESOLUTION_REJECTED_LABEL),
    )

    class Meta:
        verbose_name = 'Решение по заявке на вступление в сообщество'
        verbose_name_plural = 'Решения по заявке на вступление в сообщество'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    resolution = models.CharField(verbose_name='Решение', choices=RESOLUTION_CHOICES, max_length=20)
    community_request = models.ForeignKey(to=CommunityRequest, on_delete=models.CASCADE, related_name='resolutions')

    def is_ok(self):
        return self.resolution == self.RESOLUTION_AGREED_KEY


class Initiative(SafeDeleteModel, models.Model):
    # Время, отводимое на согласование инициативы
    APPROVAL_PERIOD_HOURS = timedelta(hours=3 * 24)
    # Минимальный процент одобрений, который должна набрать инициатива, чтобы считаться принятой
    MIN_AGREE_PERCENT = 75 / 100

    INITIATIVE_LABEL_LENGTH_LIMIT = 100

    INITIATIVE_STATUS_OPEN_KEY = 'open'
    INITIATIVE_STATUS_OPEN_LABEL = 'открыта'
    INITIATIVE_STATUS_AGREED_KEY = 'agreed'
    INITIATIVE_STATUS_AGREED_LABEL = 'принята'
    INITIATIVE_STATUS_REJECTED_KEY = 'rejected'
    INITIATIVE_STATUS_REJECTED_LABEL = 'отклонена'

    STATUS_CHOICES = (
        (INITIATIVE_STATUS_OPEN_KEY, INITIATIVE_STATUS_OPEN_LABEL),
        (INITIATIVE_STATUS_AGREED_KEY, INITIATIVE_STATUS_AGREED_LABEL),
        (INITIATIVE_STATUS_REJECTED_KEY, INITIATIVE_STATUS_REJECTED_LABEL),
    )

    class Meta:
        verbose_name = 'Инициатива'
        verbose_name_plural = 'Инициативы'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    edited_at = models.DateTimeField(verbose_name='Дата правки', auto_now=True)
    community = models.ForeignKey(to=Community, on_delete=models.CASCADE, related_name='community_initiatives')
    initiative_label = models.CharField(verbose_name='Заголовок инициативы', max_length=INITIATIVE_LABEL_LENGTH_LIMIT)
    initiative_text = models.TextField(verbose_name='Текст инициативы')
    expire_at = models.DateTimeField(default=initiative_default_expire_at)
    min_agree_percent = models.PositiveIntegerField(verbose_name='Минимальный процент одобрений',
                                                    default=MIN_AGREE_PERCENT)
    status = models.CharField(verbose_name='Статус инициативы', choices=STATUS_CHOICES, max_length=20,
                              default=INITIATIVE_STATUS_OPEN_KEY)
    involved_communities = models.ManyToManyField(to=Community, related_name='involved_communities', null=True,
                                                  blank=True)

    @property
    def messages_count(self):
        return self.initiative_messages.count()

    @property
    def agreed_count(self):
        return self.initiative_resolutions.filter(resolution=ResolutionInitiative.RESOLUTION_AGREED_KEY).count()

    @property
    def rejected_count(self):
        return self.initiative_resolutions.filter(resolution=ResolutionInitiative.RESOLUTION_REJECTED_KEY).count()

    def does_user_have_access(self, profile: Profile):
        profiles = list(self.community.get_profiles_qs())
        result = False
        if profile:
            involved_communities_qs = self.involved_communities.all()

            for involved_community in involved_communities_qs:
                profiles.append(list(involved_community.get_profiles_qs()))
            all_profiles_ids = [prf.pk for prf in profiles]
            result = profile.pk in all_profiles_ids
        return result

    def __str__(self):
        return f'{self.initiative_label} ({self.author.username}: {self.created_at.strftime("%d.%m.%Y %H:%M:%S")})'


class MessageInitiative(SafeDeleteModel, models.Model):
    class Meta:
        verbose_name = 'Сообщения инициативы'
        verbose_name_plural = 'Сообщения инициатив'

    initiative = models.ForeignKey(to=Initiative, on_delete=models.CASCADE, related_name='initiative_messages')
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    edited_at = models.DateTimeField(verbose_name='Дата правки', auto_now=True)
    message = models.TextField(verbose_name='Текст сообщения')

    def __str__(self):
        return f'{self.message[:50]} ({self.author.username}: {self.created_at.strftime("%d.%m.%Y %H:%M:%S")})'


class ResolutionInitiative(SafeDeleteModel, models.Model):
    RESOLUTION_AGREED_KEY = 'agreed'
    RESOLUTION_AGREED_LABEL = 'принята'
    RESOLUTION_REJECTED_KEY = 'rejected'
    RESOLUTION_REJECTED_LABEL = 'отклонена'

    RESOLUTION_CHOICES = (
        (RESOLUTION_AGREED_KEY, RESOLUTION_AGREED_LABEL),
        (RESOLUTION_REJECTED_KEY, RESOLUTION_REJECTED_LABEL),
    )

    class Meta:
        verbose_name = 'Решение по инициативе'
        verbose_name_plural = 'Решения по инициативе'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, db_index=True)
    resolution = models.CharField(verbose_name='Решение', choices=RESOLUTION_CHOICES, max_length=20)
    initiative = models.ForeignKey(to=Initiative, on_delete=models.CASCADE, related_name='initiative_resolutions')

    def is_ok(self):
        return self.resolution == self.RESOLUTION_AGREED_KEY
