from django.urls import re_path

from .views import MainCrowdfunding

urlpatterns = [
    re_path(r'^$', MainCrowdfunding.as_view(), name='crowdfunding'),
]
