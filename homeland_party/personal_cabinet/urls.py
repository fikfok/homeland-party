from django.urls import re_path

from .views import PersonalCabinetInvitesView, ProfileView

urlpatterns = [
    re_path(r'^invites$', PersonalCabinetInvitesView.as_view(), name='invites'),
    re_path(r'^profile$', ProfileView.as_view(), name='profile'),
]
