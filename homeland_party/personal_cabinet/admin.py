from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models.models import Profile
from .models.model_geo import Geo


@admin.register(Geo)
class GeoAdmin(admin.ModelAdmin):
    list_display = ('geo',)

    def geo(self, instance):
        from veche.models import Community

        self_label = str(instance)
        CTModel = ContentType.objects.get(model=instance.object_type.model).model_class()
        entity = CTModel.objects.get(pk=instance.object_id)
        if isinstance(entity, Community):
            community_label = entity.get_community_type_label()
            self_label += f'. {community_label} id = {instance.object_id}'
        else:
            self_label += f'. {CTModel._meta.verbose_name} id = {instance.object_id}'
        return self_label


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'user_in_geo_community',)

    def profile(self, instance):
        user_name = instance.user.username
        instance_label = f'User email: {str(instance)}. User name: {user_name}. ID = {str(instance.pk)}'
        return instance_label

    def user_in_geo_community(self, instance):
        return instance.user_in_geo_community()
