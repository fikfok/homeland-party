import copy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from invite.forms import InviteForm
from invite.helpers.email_sender import EmailSender


class PersonalCabinetInvites(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        form = InviteForm()
        context = {
            'invite_form': form,
        }
        return render(request, 'invite/invite_section.html', context)

    def post(self, request, *args, **kwargs):
        form = InviteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            email_sender = EmailSender(email=email, request=request)
            email_sender.send_email()
            return HttpResponseRedirect(reverse('personal_cabinet:invites'))
        else:
            return HttpResponse('Неверные данные')
