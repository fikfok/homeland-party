from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, F
from safedelete.models import SafeDeleteModel

from personal_cabinet.mixins.geo_mixin import GeoMixin


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
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True, db_index=True)
    type = models.CharField(verbose_name='Тип сообщества', choices=COMMUNITY_TYPE_CHOICES, max_length=50)
    max_participants = models.PositiveIntegerField(verbose_name="Максимальное количество дочерних элементов")

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

    def __str__(self):
        geo = self.get_geo()
        current_label = self.get_community_type_label()
        return f'{current_label}. Адрес: {str(geo)}'
