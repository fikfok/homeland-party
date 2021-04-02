from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from homeland_party.mixins import CustomTemplateViewMixin
from personal_cabinet.models import Profile


class MainVecheView(CustomTemplateViewMixin, TemplateView):
    template_name = 'veche_main.html'


class GeoTenView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        geo = profile.get_geo()
        user_can_create_community = profile.user_can_create_community()
        user_in_geo_community = profile.user_in_geo_community()
        context = self.get_context_data(request=request)
        extra_context = {
            'geo': geo,
            'user_can_create_community': user_can_create_community,
            'user_in_geo_community': user_in_geo_community,
            'address_text': str(geo) if geo else '',
        }
        context.update(extra_context)
        return render(request, 'veche_geo_ten.html', context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        user_can_create_community = profile.user_can_create_community()
        if user_can_create_community:
            redirect_url = request.build_absolute_uri(reverse('veche:my_geo_ten'))
            data = {'redirect_url': redirect_url}
            return JsonResponse(data, status=200)
        else:
            return HttpResponse(status=400)


class JoinGeoTenView(CustomTemplateViewMixin, TemplateView):
    template_name = 'veche_join_geo_ten.html'


class MyGeoTenView(CustomTemplateViewMixin, TemplateView):
    template_name = 'veche_my_geo_ten.html'
