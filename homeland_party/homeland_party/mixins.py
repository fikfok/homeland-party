from django.contrib.auth.mixins import LoginRequiredMixin

from personal_cabinet.models.models import Profile


class CustomTemplateViewMixin(LoginRequiredMixin):
    login_url = '/login'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = self._get_profile()
        extra_context = {
            'user': user,
            'profile': profile if profile else None,
            'user_in_geo_community': profile.user_in_geo_community() if profile else False,
            'user_can_create_geo_community': profile.user_can_create_geo_community() if profile else False,
            'user_can_join_in_geo_community': profile.user_can_join_in_geo_community() if profile else False,
            'user_has_not_geo_community_request': profile.user_has_not_geo_community_request() if profile else False,
            'did_user_create_community_request': profile.did_user_create_community_request() if profile else False,
            'does_user_have_to_approve_requests': profile.does_user_have_to_approve_requests() if profile else False,
        }
        context.update(extra_context)
        return context

    def _get_profile(self) -> Profile:
        return Profile.objects.filter(user=self.request.user).first()
