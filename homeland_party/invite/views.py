from typing import Union

from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.views.generic import TemplateView

from invite.forms import CustomSetPasswordForm
from invite.models import Invite
from personal_cabinet.models.models import Profile


class ActivateInvite(TemplateView):

    def _check_invite(self, invite_code: str) -> Union[None, HttpResponse]:
        code = escape(invite_code)
        try:
            invite = Invite.objects.get(code=code)
        except Invite.DoesNotExist:
            return HttpResponse('Неверный код приглашения', status=400)

        if invite.is_activated:
            return HttpResponse('Приглашение уже было активировано', status=400)

        if invite.expire_at < timezone.now():
            return HttpResponse('Срок приглашения истёк', status=400)
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
        email = escape(invite.email)
        user_not_exists = not User.objects.filter(email__iexact=email).exists()
        if user_not_exists:
            new_user = User(email=email)
            form = CustomSetPasswordForm(data=request.POST, user=new_user)
            if form.is_valid():
                new_user.set_password(request.POST.get('new_password1'))
                new_user.save()
                invite.is_activated = True
                invite.password_changed = True
                invite.save()
                Profile.objects.create(user=new_user)
                login(request=request, user=new_user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect(reverse('home'))
            else:
                context = {'form': form}
                return render(request, 'activate_invite.html', context=context)
        else:
            return HttpResponse('Такой пользователь уже создан', status=400)


