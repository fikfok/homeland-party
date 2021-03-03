from django.contrib import admin
from django.urls import re_path

from .views import MainVeche

urlpatterns = [
    re_path(r'^$', MainVeche.as_view(), name='main_veche'),
]
