from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MainCrowdsourcing(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'crowdsourcing_main.html'