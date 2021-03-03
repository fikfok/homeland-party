from django.contrib import admin
from django.urls import path, re_path, include

from .views import HomePage
import veche.urls as veche_urls
# import homeland_party.veche.urls as veche_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$', HomePage.as_view(), name='home'),
    re_path(r'^veche/', include((veche_urls, 'veche'), namespace='veche')),
]
