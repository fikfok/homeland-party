from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from invite.forms import InviteForm
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
            return HttpResponse('Invalid form data')


class ActivateInvite(TemplateView):

    def get(self, request, *args, **kwargs):
        invite_code = kwargs.get('invite_code')
        try:
            invite = Invite.objects.filter(code=invite_code)
        except Exception:
            return HttpResponse('Invalid invite code')

        form = SetPasswordForm(request.user)
        context = {
            'form': form
        }
        return render(request, 'activate_invite.html', context=context)

    def post(self, request, *args, **kwargs):

