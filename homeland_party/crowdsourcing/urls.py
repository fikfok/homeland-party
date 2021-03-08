from django.urls import re_path

from .views import MainCrowdsourcing

urlpatterns = [
    re_path(r'^$', MainCrowdsourcing.as_view(), name='crowdsourcing'),
]
