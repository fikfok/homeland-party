from django.contrib.contenttypes.models import ContentType

from personal_cabinet.models.model_geo import Geo


class GeoMixin:
    def geo_exists(self) -> bool:
        object_type = ContentType.objects.get_for_model(self.__class__)
        return Geo.objects.filter(object_type=object_type, object_id=self.pk).exists()

    def get_geo(self):
        object_type = ContentType.objects.get_for_model(self.__class__)
        return Geo.objects.filter(object_type=object_type, object_id=self.pk).first() if self.geo_exists() else None
