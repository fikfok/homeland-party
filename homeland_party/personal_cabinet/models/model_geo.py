from django.contrib.contenttypes.models import ContentType
from django.db import models


class Geo(models.Model):
    class Meta:
        verbose_name = 'Гео'
        verbose_name_plural = 'Гео'

    object_type = models.ForeignKey(verbose_name='Тип сущности', to=ContentType, related_name='related_object_type',
                                    on_delete=models.DO_NOTHING, null=True, blank=True)
    object_id = models.PositiveIntegerField(verbose_name='ID сущности', null=True, blank=True)
    postal_code = models.CharField(verbose_name='Почтовый индекс', max_length=10, null=True, blank=True)
    country = models.CharField(verbose_name='Страна', max_length=300, null=True, blank=True)
    country_iso_code = models.CharField(verbose_name='ISO код страны', max_length=5, null=True, blank=True)
    federal_district = models.CharField(verbose_name='Федеральный округ', max_length=100, null=True, blank=True)
    region_fias_id = models.CharField(verbose_name='ФИАС ID области', max_length=100, null=True, blank=True)
    region_iso_code = models.CharField(verbose_name='ISO код области', max_length=10, null=True, blank=True)
    region_type = models.CharField(verbose_name='Тип области', max_length=100, null=True, blank=True)
    region = models.CharField(verbose_name='Название области', max_length=300, null=True, blank=True)
    area_fias_id = models.CharField(verbose_name='ФИАС ID района', max_length=100, null=True, blank=True)
    area_type = models.CharField(verbose_name='Тип района', max_length=100, null=True, blank=True)
    area = models.CharField(verbose_name='Название района', max_length=300, null=True, blank=True)
    city_fias_id = models.CharField(verbose_name='ФИАС ID города', max_length=100, null=True, blank=True)
    city_type = models.CharField(verbose_name='Тип города', max_length=50, null=True, blank=True)
    city = models.CharField(verbose_name='Название города', max_length=300, null=True, blank=True)
    city_district_fias_id = models.CharField(verbose_name='ФИАС ID района города', max_length=100, null=True,
                                             blank=True)
    city_district_type = models.CharField(verbose_name='Тип района города', max_length=50, null=True, blank=True)
    city_district = models.CharField(verbose_name='Название района города', max_length=300, null=True, blank=True)
    settlement_fias_id = models.CharField(verbose_name='ФИАС ID населённого пункта', max_length=100, null=True,
                                          blank=True)
    settlement_type = models.CharField(verbose_name='Тип населённого пункта', max_length=50, null=True, blank=True)
    settlement = models.CharField(verbose_name='Название населённого пункта', max_length=300, null=True, blank=True)
    street_fias_id = models.CharField(verbose_name='ФИАС ID улицы', max_length=100, null=True, blank=True)
    street_type = models.CharField(verbose_name='Тип улицы', max_length=50, null=True, blank=True)
    street = models.CharField(verbose_name='Название улицы', max_length=300, null=True, blank=True)
    house_fias_id = models.CharField(verbose_name='ФИАС ID дома', max_length=100, null=True, blank=True)
    house_type = models.CharField(verbose_name='Тип дома', max_length=50, null=True, blank=True)
    house = models.CharField(verbose_name='Номер дома', max_length=50, null=True, blank=True)
    block_type = models.CharField(verbose_name='Тип строения', max_length=50, null=True, blank=True)
    block = models.CharField(verbose_name='Номер строения', max_length=50, null=True, blank=True)
    fias_id = models.CharField(verbose_name='ФИАС ID адреса', max_length=100, null=True, blank=True)
    fias_code = models.CharField(verbose_name='ФИАС код адреса', max_length=100, null=True, blank=True)
    fias_level = models.CharField(verbose_name='Уровень ФИАС кода', max_length=10, null=True, blank=True)

    geo_lat = models.FloatField(verbose_name='Долгота', null=True, blank=True)
    geo_lon = models.FloatField(verbose_name='Широта', null=True, blank=True)

    def __str__(self):
        labels = [
            self.country,
            f'{self.region} {self.region_type}.' if self.region and self.region_type else '',
            f'{self.area} {self.area_type}' if self.area and self.area_type else '',
            f'{self.city_type}. {self.city}' if self.city_type and self.city else '',
            f'{self.city_district_type} {self.city_district}' if self.city_district_type and self.city_district else '',
            f'{self.settlement_type}. {self.settlement}' if self.settlement_type and self.settlement else '',
            f'{self.street_type}. {self.street}' if self.street_type and self.street else '',
            f'{self.house_type}. {self.house}' if self.house_type and self.house else '',
            f'{self.block_type} {self.block}' if self.block_type and self.block else ''
        ]
        labels = [lbl for lbl in labels if lbl]
        labels = ', '.join(labels)
        return labels
