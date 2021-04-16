from django.contrib.auth.mixins import LoginRequiredMixin

from personal_cabinet.models.models import Profile


class CustomTemplateViewMixin(LoginRequiredMixin):
    login_url = '/login'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = Profile.objects.filter(user=user).first()
        extra_context = {
            'user': user,
            'profile': profile if profile else None,
            'user_in_geo_community': profile.user_in_geo_community() if profile else False,
            'user_can_create_geo_community': profile.user_can_create_geo_community() if profile else False,
            'user_can_join_in_geo_community': profile.user_can_join_in_geo_community() if profile else False,
            'user_has_not_geo_community_request': profile.user_has_not_geo_community_request() if profile else False,
        }
        context.update(extra_context)
        return context
