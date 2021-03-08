from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MainVeche(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'veche_main.html'

