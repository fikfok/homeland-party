from django.urls import re_path

from .views import MainVecheView, GeoTenView, JoinGeoTenView

urlpatterns = [
    re_path(r'^$', MainVecheView.as_view(), name='veche'),
    re_path(r'^geo_ten$', GeoTenView.as_view(), name='geo_ten'),
    re_path(r'^join_geo_ten$', JoinGeoTenView.as_view(), name='join_geo_ten'),
]
