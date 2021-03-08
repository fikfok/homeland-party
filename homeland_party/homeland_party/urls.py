from django.contrib import admin
from django.urls import path, re_path, include

from .views import HomePage, LoginPage
import veche.urls as veche_urls
import crowdfunding.urls as crowdfunding_urls
import crowdsourcing.urls as crowdsourcing_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^login/$', LoginPage.as_view(), name="login"),
    re_path(r'^$', HomePage.as_view(), name='home'),
    re_path(r'^veche/', include((veche_urls, 'veche'), namespace='veche')),
    re_path(r'^crowdfunding/', include((crowdfunding_urls, 'crowdfunding'), namespace='crowdfunding')),
    re_path(r'^crowdsourcing/', include((crowdsourcing_urls, 'crowdsourcing'), namespace='crowdsourcing')),
]
