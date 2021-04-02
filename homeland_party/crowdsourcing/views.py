from django.views.generic import TemplateView

from homeland_party.mixins import CustomTemplateViewMixin


class MainCrowdsourcing(CustomTemplateViewMixin, TemplateView):
    template_name = 'crowdsourcing_main.html'
