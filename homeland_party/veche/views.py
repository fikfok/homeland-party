from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.views import View
from django.views.generic import TemplateView

from homeland_party.const import MAP_WIDTH_PX, MAP_HEIGHT_PX, YANDEX_API_KEY
from homeland_party.mixins import CustomTemplateViewMixin
from personal_cabinet.models.models import Profile
from veche.models import Community, CommunityRequest, RequestStats, RequestResolution


class MainVecheView(CustomTemplateViewMixin, TemplateView):
    template_name = 'veche_main.html'


class GeoTenView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = self._get_profile()
        if not profile:
            return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        geo = profile.get_geo()
        context = self.get_context_data()
        extra_context = {
            'geo': geo,
            'address_text': str(geo) if geo else '',
        }
        context.update(extra_context)
        return render(request, 'veche_geo_ten.html', context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = self._get_profile()
        if not profile:
            return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        user_can_create_geo_community = profile.user_can_create_geo_community()
        if user_can_create_geo_community:
            community_data = {
                'author': user,
                'type': Community.COMMUNITY_TYPE_TEN_KEY,
                'max_participants': Community.MAX_PARTICIPANTS[Community.COMMUNITY_TYPE_TEN_KEY],
            }
            community = Community.objects.create(**community_data)
            community_geo = profile.get_geo()
            community_geo.pk = None
            community_geo.object_type = ContentType.objects.get_for_model(Community)
            community_geo.object_id = community.pk
            community_geo.save()
            profile.geo_community.add(community)
            profile.save()

            redirect_url = request.build_absolute_uri(reverse('veche:my_geo_ten'))
            data = {'redirect_url': redirect_url}
            response = JsonResponse(data, status=200)
        else:
            response = HttpResponse('Вы не можете создать географическую десятку', status=400)
        return response


class JoinGeoTenView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if context['user_has_not_geo_community_request']:
            profile = self._get_profile()
            if not profile:
                return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

            geo = profile.get_geo()
            geo_tens_for_join_qs = Community.get_geo_tens_for_join()
            extra_context = {
                'geo': geo,
                'geo_tens_for_join_qs': geo_tens_for_join_qs,
                'map_width': MAP_WIDTH_PX,
                'map_height': MAP_HEIGHT_PX,
            }
            context.update(extra_context)
            response = render(request, 'veche_join_geo_ten.html', context=context)
        else:
            response = HttpResponse('Вы уже подали заявку на вступление в географическую десятку', status=400)
        return response

    def post(self, request, geo_ten_id):
        context = self.get_context_data()
        if context['user_has_not_geo_community_request']:
            geo_ten = Community.objects.filter(pk=geo_ten_id).first()
            if geo_ten:
                is_geo_ten_open = geo_ten.is_geo_ten_open()
                if is_geo_ten_open:
                    comment = escape(request.POST.get('comment'))[:1000]
                    CommunityRequest.objects.create(author=request.user, community=geo_ten, comment=comment)
                    response = JsonResponse({}, status=200)
                else:
                    response = JsonResponse({'message': 'Географическая десятка уже укомплектована'}, status=400)
            else:
                response = JsonResponse({'message': 'Заявка подана на несуществующую географическую десятку'},
                                        status=400)
        else:
            response = JsonResponse({'message': 'Вы уже подали заявку на вступление в географическую десятку'},
                                    status=400)
        return response


class GeoCommunityParticipiants(CustomTemplateViewMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            geo_community = Community.objects.get(pk=request.GET.get('geo_community_id'))
        except Exception:
            result = []
            status = 400
        else:
            profiles_qs = geo_community.get_profiles_qs()
            if profiles_qs.exists():
                result = []
                for profile in profiles_qs:
                    card_data = profile.get_card_data()
                    data = {
                        'user_name': card_data['user_name'],
                        'first_name': card_data['first_name'],
                        'last_name': card_data['last_name'],
                        'profile_id': profile.pk,
                        'user_id': profile.user.pk,
                    }
                    result.append(data)
                status = 200
            else:
                result = []
                status = 400

        return JsonResponse(result, status=status, safe=False)


class MyGeoTenView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        profile = self._get_profile()
        geo_ten_community = profile.get_geo_ten_communities_qs().first() if profile.user_in_geo_community() else None
        extra_context = {
            'geo_ten_community': geo_ten_community
        }
        context.update(extra_context)

        return render(request, 'veche_my_geo_ten.html', context=context)


class UserCardView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        response = render(request, 'veche_user_card.html', context=context)
        return response


class MyRequestsView(CustomTemplateViewMixin, TemplateView):
    AGREE_URL_ALIAS = 'agree_request'
    REJECT_URL_ALIAS = 'reject_request'

    def get(self, request, *args, **kwargs):
        profile = self._get_profile()
        if not profile:
            return HttpResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        requests_user_need_to_approve = profile.get_requests_user_need_to_approve()
        created_by_user_community_request = profile.get_created_by_user_community_request()
        created_by_user_community_request_solved = profile.get_created_by_user_community_request_solved()
        user_resolutions = profile.get_user_resolutions()
        if created_by_user_community_request:
            created_by_user_community_request_stats = created_by_user_community_request.get_request_stats()
        else:
            created_by_user_community_request_stats = RequestStats(0, 0, 0)
        context = self.get_context_data()
        extra_context = {
            'requests_user_need_to_approve': requests_user_need_to_approve,
            'created_by_user_community_request': created_by_user_community_request,
            'created_by_user_community_request_stats': created_by_user_community_request_stats,
            'created_by_user_community_request_solved': created_by_user_community_request_solved,
            'user_resolutions': user_resolutions,
        }
        context.update(extra_context)
        return render(request, 'veche_my_requests.html', context=context)

    def post(self, request):
        user = request.user
        profile = self._get_profile()
        if not profile:
            return JsonResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        request_id = request.POST.get('request_id')
        try:
            request_id = int(request_id)
        except Exception:
            response = JsonResponse({'message': 'Неверный идентификатор заявки'}, status=400)
        else:
            if request_id:
                try:
                    community_request = CommunityRequest.objects.get(pk=request_id)
                except Exception:
                    response = JsonResponse({'message': 'Нельзя согласовать заявку, т.к. переданы неверные данные'},
                                            status=400)
                else:
                    is_it_my_request_id = profile.is_it_my_request(some_request=community_request)
                    if is_it_my_request_id:
                        did_user_resolve_request = profile.did_user_resolve_request(community_request=community_request)

                        if did_user_resolve_request:
                            response = JsonResponse({'message': 'Данная заявка вами уже согласована'}, status=400)
                        else:
                            current_url_alias = request.resolver_match.url_name
                            if current_url_alias == self.AGREE_URL_ALIAS:
                                self._agree_request(community_request=community_request, user=user)
                            if current_url_alias == self.REJECT_URL_ALIAS:
                                self._reject_request(community_request=community_request, user=user)
                            response = JsonResponse({'message': 'Заявка успешно обработана'}, status=200)

                            if current_url_alias not in [self.AGREE_URL_ALIAS, self.REJECT_URL_ALIAS]:
                                response = JsonResponse({'message': 'Неверный запрос'}, status=400)
                    else:
                        response = JsonResponse({'message': 'Нельзя согласовать чужую заявку'}, status=400)
            else:
                response = JsonResponse({'message': 'Нельзя согласовать заявку, т.к. переданы неверные данные'},
                                        status=400)
        return response

    def _agree_request(self, community_request, user):
        RequestResolution.objects.create(author=user, resolution=RequestResolution.RESOLUTION_AGREED_KEY,
                                         community_request=community_request)
        did_all_participiants_resolve = community_request.did_all_participants_resolve()
        does_request_have_reject = community_request.does_request_have_reject()
        if does_request_have_reject:
            community_request.status = CommunityRequest.REQUEST_STATUS_REJECTED_KEY
            community_request.save()
        else:
            if did_all_participiants_resolve:
                with transaction.atomic():
                    community_request.status = CommunityRequest.REQUEST_STATUS_AGREED_KEY
                    community_request.save()
                    profile = Profile.objects.get(user=community_request.author)
                    profile.geo_community.add(community_request.community)
                    profile.save()

    def _reject_request(self, community_request, user):
        RequestResolution.objects.create(author=user, resolution=RequestResolution.RESOLUTION_REJECTED_KEY,
                                         community_request=community_request)
        community_request.status = CommunityRequest.REQUEST_STATUS_REJECTED_KEY
        community_request.save()
