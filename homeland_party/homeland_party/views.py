from django.template import RequestContext
from django.views import generic


class HomePage(generic.TemplateView, RequestContext):
    template_name = 'home.html'

    # def get_template_names(self):
    #     if self.request.user.is_authenticated:
    #         return 'home.html'
    #     return "landing.html"
