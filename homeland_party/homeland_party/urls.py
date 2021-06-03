from django.contrib import admin
from django.urls import path, re_path, include

from homeland_party.views import HomePage, LoginPage #, LogoutPage
import veche.urls as veche_urls
import crowdfunding.urls as crowdfunding_urls
import crowdsourcing.urls as crowdsourcing_urls
import invite.urls as invite_urls
import personal_cabinet.urls as personal_cabinet_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^login/$', LoginPage.as_view(), name="login"),
    re_path(r'^$', HomePage.as_view(), name='home'),
    re_path(r'^veche/', include((veche_urls, 'veche'), namespace='veche')),
    re_path(r'^crowdfunding/', include((crowdfunding_urls, 'crowdfunding'), namespace='crowdfunding')),
    re_path(r'^crowdsourcing/', include((crowdsourcing_urls, 'crowdsourcing'), namespace='crowdsourcing')),
    re_path(r'^invite/', include((invite_urls, 'invite'), namespace='invite')),
    re_path(r'^personal_cabinet/', include((personal_cabinet_urls, 'personal_cabinet'), namespace='personal_cabinet')),
    # re_path(r'^logout/', LogoutPage.as_view(), name="logout"),
]
