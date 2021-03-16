from datetime import datetime
from typing import Union

from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from invite.forms import InviteForm, CustomSetPasswordForm
from invite.helpers.email_sender import EmailSender
from invite.models import Invite


class MainInvite(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def post(self, request, *args, **kwargs):
        form = InviteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            email_sender = EmailSender(email=email, request=request)
            email_sender.send_email()
            clear_form = InviteForm()
            return render(request, 'personal_cabinet_main.html', {'invite_form': clear_form})
        else:
            return HttpResponse('Неверные данные')


class ActivateInvite(TemplateView):

    def _check_invite(self, invite_code: str) -> Union[None, HttpResponse]:
        try:
            invite = Invite.objects.get(code=invite_code)
        except Invite.DoesNotExist:
            return HttpResponse('Неверный код приглашения')

        if invite.is_activated:
            return HttpResponse('Приглашение уже было активировано')

        if invite.expire_at < timezone.now():
            return HttpResponse('Срок приглашения истёк')
        return None

    def get(self, request, *args, **kwargs):
        invite_code = kwargs.get('invite_code')
        response = self._check_invite(invite_code=invite_code)
        if response:
            return response

        form = SetPasswordForm(request.user)
        context = {
            'form': form,
            'password_min_len': CustomSetPasswordForm.PASSWORD_MIN_LEN
        }
        return render(request, 'activate_invite.html', context=context)

    def post(self, request, *args, **kwargs):
        invite_code = kwargs.get('invite_code')
        response = self._check_invite(invite_code=invite_code)
        if response:
            return response

        invite = Invite.objects.get(code=invite_code)
        user_not_exists = not User.objects.filter(email__iexact=invite.email).exists()
        if user_not_exists:
            new_user = User(username=invite.email, email=invite.email)
            form = CustomSetPasswordForm(data=request.POST, user=new_user)
            if form.is_valid():
                new_user.set_password(request.POST.get('new_password1'))
                new_user.save()
                invite.is_activated = True
                invite.password_changed = True
                invite.save()
                login(request=request, user=new_user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect(reverse('home'))
            else:
                context = {'form': form}
                return render(request, 'activate_invite.html', context=context)
        else:
            return HttpResponse('Такой пользователь уже создан')


