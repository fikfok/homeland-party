from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from invite.forms import InviteForm
from invite.helpers.email_sender import EmailSender


class MainInvite(LoginRequiredMixin, TemplateView):
    login_url = '/login'

    def get(self, request, *args, **kwargs):
        form = InviteForm()
        return render(request, 'invite_main.html', {'invite_form': form})

    def post(self, request, *args, **kwargs):
        form = InviteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd['email']
            email_sender = EmailSender(email=email, request=request)
            email_sender.send_email()
            clear_form = InviteForm()
            return render(request, 'invite_main.html', {'invite_form': clear_form})
        else:
            return HttpResponse('Invalid form data')


class ActivateInvite(TemplateView):
    def get(self, request, *args, **kwargs):
        form = InviteForm()
        return render(request, 'invite_main.html', {'invite_form': form})
