from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from personal_cabinet.models import Profile


class MainVecheView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'veche_main.html'


class GeoTenView(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        geo = profile.get_geo()
        user_can_create_community = profile.user_can_create_community()
        user_in_geo_community = profile.user_in_geo_community()
        context = {
            'geo': geo,
            'user_can_create_community': user_can_create_community,
            'user_in_geo_community': user_in_geo_community,
            'address_text': str(geo) if geo else '',
        }
        return render(request, 'veche_geo_ten.html', context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        user_can_create_community = profile.user_can_create_community()
        if user_can_create_community:
            status = 200
        else:
            status = 400
        return HttpResponse(status=status)

    def _can_create_ten(self, request):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        ten_does_not_exists = not profile.geo_community.all().exists()
        geo = profile.geo if profile else None

        can_create_ten = False
        if geo and ten_does_not_exists:
            can_create_ten = True
        return can_create_ten


class JoinGeoTenView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'veche_join_geo_ten.html'
