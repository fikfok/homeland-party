from django.urls import re_path

from .views import PersonalCabinetInvites

urlpatterns = [
    re_path(r'^invites$', PersonalCabinetInvites.as_view(), name='invites'),
]
