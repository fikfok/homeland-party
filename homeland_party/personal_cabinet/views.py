from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from invite.forms import InviteForm
from invite.helpers.email_sender import EmailSender
from invite.models import Invite


class PersonalCabinetInvites(LoginRequiredMixin, TemplateView):
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
