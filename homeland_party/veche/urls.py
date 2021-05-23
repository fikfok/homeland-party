from django.urls import re_path

from .views import MainVecheView, GeoTenView, JoinGeoTenView, MyGeoTenView, GeoCommunityParticipiants, UserCardView, \
    MyRequestsView, GeoTenInitiatives

urlpatterns = [
    re_path(r'^$', MainVecheView.as_view(), name='veche'),
    re_path(r'^geo_ten$', GeoTenView.as_view(), name='geo_ten'),
    re_path(r'^geo_community_participiants$', GeoCommunityParticipiants.as_view(), name='geo_community_participiants'),
    re_path(r'^my_geo_ten$', MyGeoTenView.as_view(), name='my_geo_ten'),
    re_path(r'^join_geo_ten$', JoinGeoTenView.as_view(), name='join_geo_ten'),
    re_path(r'^join_geo_ten/(?P<geo_ten_id>[0-9]+)$', JoinGeoTenView.as_view(), name='join_geo_ten'),
    re_path(r'^user_card/(?P<user_id>[0-9]+)$', UserCardView.as_view(), name='user_card'),
    re_path(r'^my_requests$', MyRequestsView.as_view(), name='my_requests'),
    re_path(r'^my_requests/agree$', MyRequestsView.as_view(), name='agree_request'),
    re_path(r'^my_requests/reject$', MyRequestsView.as_view(), name='reject_request'),
    re_path(r'^geo_ten_initiatives$', GeoTenInitiatives.as_view(), name='geo_ten_initiatives'),
]
