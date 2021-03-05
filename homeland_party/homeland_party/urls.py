from django.contrib import admin
from django.urls import path, re_path, include

from .views import HomePage, user_login
import veche.urls as veche_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    # re_path(r'^login/$', LoginView.as_view(), name="login"),
    re_path(r'^login/$', user_login, name="login"),
    re_path(r'^$', HomePage.as_view(), name='home'),
    re_path(r'^veche/', include((veche_urls, 'veche'), namespace='veche')),
]
