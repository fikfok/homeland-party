from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MainCrowdfunding(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'crowdfunding_main.html'