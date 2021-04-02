from django.views.generic import TemplateView

from homeland_party.mixins import CustomTemplateViewMixin


class MainCrowdfunding(CustomTemplateViewMixin, TemplateView):
    template_name = 'crowdfunding_main.html'
