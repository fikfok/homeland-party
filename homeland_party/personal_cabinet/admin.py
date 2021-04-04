from django.contrib import admin

from .models import Profile
from .model_geo import Geo

admin.site.register(Profile)
admin.site.register(Geo)
