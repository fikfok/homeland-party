from django.contrib.auth.mixins import LoginRequiredMixin

from personal_cabinet.models import Profile


class CustomTemplateViewMixin(LoginRequiredMixin):
    login_url = '/login'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        request = context.get('request')
        if request:
            user = request.user
            profile = Profile.objects.filter(user=user).first()
            context['user_in_geo_ten'] = profile.user_in_geo_community() if profile else False
        return context
