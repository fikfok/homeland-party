from django.urls import re_path

from .views import PersonalCabinet

urlpatterns = [
    re_path(r'^$', PersonalCabinet.as_view(), name='personal_cabinet'),
]
