import copy

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.views import View
from django.views.generic import TemplateView

from homeland_party.const import YANDEX_API_KEY, MAP_WIDTH_PX, MAP_HEIGHT_PX, DEFAULT_LAT, DEFAULT_LON
from homeland_party.mixins import CustomTemplateViewMixin
from homeland_party.settings import geocoder

from invite.forms import InviteForm
from invite.helpers.email_sender import EmailSender
from invite.models import Invite
from personal_cabinet.forms import GeoForm, ProfileForm
from personal_cabinet.models.models import Profile


class PersonalCabinetInvitesView(CustomTemplateViewMixin, TemplateView):

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
        context = self.get_context_data()
        extra_context = {
            'invite_form': form,
            'send_invites_qs': send_invites_qs,
            'invites_limit': invites_limit,
            'invites_remainder': invites_remainder,
            'show_form': show_form,
        }
        context.update(extra_context)
        return render(request, 'invite/invite_section.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        send_invites_qs = self._get_send_invites_qs(request=request)
        invites_remainder = user.profile.max_invites - send_invites_qs.count()
        if not user.is_superuser and invites_remainder <= 0:
            return HttpResponse('Лимит приглашений исчерпан', status=400)

        does_invite_exist_with_email = self._does_invite_exist_with_email(request=request)
        if does_invite_exist_with_email:
            return HttpResponse("Приглашение с таким email'ом уже создано и активировано", status=400)

        form = InviteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = escape(cd['email'])
            email_sender = EmailSender(email=email, request=request)
            email_sender.send_email()
            return HttpResponseRedirect(reverse('personal_cabinet:invites'))
        else:
            return HttpResponse('Неверные данные', status=400)

    def _get_send_invites_qs(self, request):
        return Invite.objects.filter(author=request.user)

    def _does_invite_exist_with_email(self, request) -> bool:
        email = request.POST.get('email', '')
        return Invite.objects.filter(email__iexact=email, is_activated=True).exists()


class ProfileView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = self._get_profile()
        if not profile:
            return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        geo = profile.get_geo()
        data = profile.get_form_data()
        profile_form = ProfileForm(data=data, user_pk=user.pk, is_post_request=False)

        context = self.get_context_data()
        extra_context = {
            'profile_form': profile_form,
            'address_text': str(geo) if geo else '',
        }
        context.update(extra_context)
        return render(request, 'profile.html', context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile_form = ProfileForm(data=request.POST, user_pk=user.pk, is_post_request=True)
        if profile_form.is_valid():
            self._update_user(profile_form, user)
            self._update_profile(profile_form, user)
            response = HttpResponseRedirect(reverse('personal_cabinet:profile'))
        else:
            profile_form = ProfileForm(data=request.POST, user_pk=user.pk, is_post_request=True)
            context = self.get_context_data()
            profile = self._get_profile()
            if not profile:
                return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

            geo = profile.get_geo()
            extra_context = {
                'profile_form': profile_form,
                'address_text': str(geo) if geo else '',
            }
            context.update(extra_context)
            response = render(request, 'profile.html', context=context)
        return response

    def _update_profile(self, profile_form, user):
        profile = self._get_profile()
        if profile:
            birth_date = profile_form.cleaned_data['birth_date']
            if birth_date:
                profile.birth_date = profile_form.cleaned_data['birth_date']
            else:
                profile.birth_date = None
            self._update_geo(profile, profile_form)
            profile.save()

    def _update_geo(self, profile, profile_form):
        latitude = profile_form.cleaned_data.get('latitude')
        longitude = profile_form.cleaned_data.get('longitude')
        if latitude and longitude:
            # Если пришли координаты, то удаляем старый адрес если он есть
            if profile.geo_exists():
                geo = profile.get_geo()
                geo.delete()
            geo_data = geocoder.get_geo_data(latitude=latitude, longitude=longitude)
            geo_data['object_type'] = ContentType.objects.get_for_model(Profile)
            geo_data['object_id'] = profile.pk
            geo_form = GeoForm(geo_data)
            geo_form.save()

    def _update_user(self, profile_form, user):
        user.username = escape(profile_form.cleaned_data['user_name'])
        user.first_name = escape(profile_form.cleaned_data['first_name'])
        user.last_name = escape(profile_form.cleaned_data['last_name'])
        user.save()


class GeoCodeView(CustomTemplateViewMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        geocode = escape(request.GET.get('geocode', ''))
        address = geocoder.get_geo_data(geocode=geocode)
        geo_data = copy.deepcopy(address)
        geo_data['object_type'] = ContentType.objects.get_for_model(Profile)
        geo_data['object_id'] = profile.pk
        geo_form = GeoForm(geo_data)
        if address and geo_form.is_valid():
            result = str(geo_form.instance)
            status = 200
        else:
            result = geocoder.WRONG_GEO_MSG
            status = 400
        return HttpResponse(result, status=status)
