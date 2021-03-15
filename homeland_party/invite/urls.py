from django.urls import re_path

from .views import MainInvite, ActivateInvite

urlpatterns = [
    re_path(r'^$', MainInvite.as_view(), name='invite'),
    re_path(r'^(?P<invite_code>[\w\d-]+)$', ActivateInvite.as_view(), name='activate_invite'),
]
