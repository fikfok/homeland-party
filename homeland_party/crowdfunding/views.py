from django.shortcuts import render
from django.views.generic import TemplateView

from homeland_party.mixins import CustomTemplateViewMixin


class MainCrowdfunding(CustomTemplateViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, 'crowdfunding_main.html', context=context)
