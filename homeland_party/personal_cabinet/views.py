from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from homeland_party.const import YANDEX_API_KEY, MAP_WIDTH_PX, MAP_HEIGHT_PX

from invite.forms import InviteForm
from invite.helpers.email_sender import EmailSender
from invite.models import Invite
from personal_cabinet.forms import GeoForm, ProfileForm
from personal_cabinet.helpers.geocoder import Geocoder


# Реализован с кешем, потому объявлять надо глобально
geocoder = Geocoder()


class PersonalCabinetInvitesView(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        user = request.user
        send_invites_qs = self._get_send_invites_qs(request=request)
        if user.is_superuser:
            invites_limit = 'Не ограничено'
            invites_remainder = 'Не ограничено'
            show_form = True
        else:
            invites_limit = str(user.profile.max_invites)
            invites_remainder = user.profile.max_invites - send_invites_qs.count()
            show_form = user.profile.max_invites - send_invites_qs.count() > 0

        form = InviteForm()
        context = {
            'invite_form': form,
            'send_invites_qs': send_invites_qs,
            'invites_limit': invites_limit,
            'invites_remainder': invites_remainder,
            'show_form': show_form,
        }
        return render(request, 'invite/invite_section.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        send_invites_qs = self._get_send_invites_qs(request=request)
        invites_remainder = user.profile.max_invites - send_invites_qs.count()
        if not user.is_superuser and invites_remainder <= 0:
            return HttpResponse('Лимит приглашений исчерпан')

        does_invite_exist_with_email = self._does_invite_exist_with_email(request=request)
        if does_invite_exist_with_email:
            return HttpResponse("Приглашение с таким email'ом уже создано и активировано")

        form = InviteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            email_sender = EmailSender(email=email, request=request)
            email_sender.send_email()
            return HttpResponseRedirect(reverse('personal_cabinet:invites'))
        else:
            return HttpResponse('Неверные данные')

    def _get_send_invites_qs(self, request):
        return Invite.objects.filter(author=request.user)

    def _does_invite_exist_with_email(self, request) -> bool:
        email = request.POST.get('email', '')
        return Invite.objects.filter(email__iexact=email, is_activated=True).exists()


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        profile_form = ProfileForm()

        context = {
            'profile_form': profile_form,
            'yandex_api_key': YANDEX_API_KEY,
            'map_width': MAP_WIDTH_PX,
            'map_height': MAP_HEIGHT_PX,
        }
        return render(request, 'profile.html', context=context)


class GeoCodeView(LoginRequiredMixin, View):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        geocode = request.GET.get('geocode', '')
        geo_data = geocoder.get_geo_data(geocode=geocode)
        geo_form = GeoForm(geo_data)
        if geo_data and geo_form.is_valid():
            geo_form.save()
            result = str(geo_form.instance)
            status = 200
        else:
            result = (
                'Нельзя определить адрес по данным координатам. '
                'Попробуйте, пожалуйста, выбрать координаты ближе к населённому пункту.'
            )
            status = 400
        return HttpResponse(result, status=status)
