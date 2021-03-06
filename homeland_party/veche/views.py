from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
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
from veche.mixins import InitiativeViewMixis
from veche.models import Community, CommunityRequest, RequestStats, RequestResolution, Initiative, MessageInitiative, \
    ResolutionInitiative


class MainVecheView(CustomTemplateViewMixin, TemplateView):
    template_name = 'veche_main.html'


class GeoTenView(CustomTemplateViewMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = self._get_profile()
        if not profile:
            return HttpResponse('Отсутствует профиль пользователя', status=400)

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
            return HttpResponse('Отсутствует профиль пользователя', status=400)

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
                return HttpResponse('Отсутствует профиль пользователя', status=400)

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
        community = profile.get_first_geo_ten_community()
        profiles = community.get_profiles_qs() if community else []
        extra_context = {
            'community': community,
            'profiles': profiles,
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
            return HttpResponse('Отсутствует профиль пользователя', status=400)

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
                            if community_request.community.is_geo_ten_open():
                                current_url_alias = request.resolver_match.url_name
                                if current_url_alias == self.AGREE_URL_ALIAS:
                                    self._agree_request(community_request=community_request, user=user)
                                if current_url_alias == self.REJECT_URL_ALIAS:
                                    self._reject_request(community_request=community_request, user=user)
                                response = JsonResponse({'message': 'Заявка успешно обработана'}, status=200)

                                if current_url_alias not in [self.AGREE_URL_ALIAS, self.REJECT_URL_ALIAS]:
                                    response = JsonResponse({'message': 'Неверный запрос'}, status=400)
                            else:
                                response = JsonResponse({'message': 'Десятка уже укомплектована'}, status=400)
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


class GeoTenInitiativesView(CustomTemplateViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        community = context['profile'].get_first_geo_ten_community()
        initiatives = community.get_initiatives if community else []
        initiative_label_length_limit = Initiative.INITIATIVE_LABEL_LENGTH_LIMIT
        extra_context = {
            'community': community,
            'initiatives': initiatives,
            'initiative_label_length_limit': initiative_label_length_limit,
        }
        context.update(extra_context)
        response = render(request, 'veche_geo_ten_initiatives.html', context=context)
        return response

    def post(self, request):
        initiative_label = escape(request.POST.get('label'))
        initiative_text = escape(request.POST.get('text'))
        if len(initiative_label) * len(initiative_text) == 0:
            return JsonResponse({'message': 'Заголовок и текст инициативы должны быть обязателно указаны'}, status=400)

        profile = self._get_profile()
        if not profile:
            return JsonResponse({'message': 'Отсутствует профиль пользователя'}, status=400)

        community = profile.get_first_geo_ten_community()
        community_is_ok = bool(community) and community.is_possible_to_create_initiative()
        if profile.user_in_geo_community() and community_is_ok:
            data = {
                'author': request.user,
                'community': community,
                'initiative_label': initiative_label,
                'initiative_text': initiative_text,
            }
            initiative = Initiative.objects.create(**data)
            response = JsonResponse({'message': 'Инициатива успешно создана'}, status=200)
        else:
            msg = (
                'Создать инициативу нельзя. Либо пользователь не состоит в гео десятке либо гео дестка не '
                'укомплектована'
            )
            response = JsonResponse({'message': msg}, status=200)
        return response


class InitiativeView(InitiativeViewMixis, CustomTemplateViewMixin, TemplateView):
    MESSAGES_ON_PAGE = 10

    def get(self, request, *args, **kwargs):
        initiative_id = kwargs.get('initiative_id')
        response_400 = self._check_initiative(initiative_id)
        if response_400:
            return response_400

        initiative = Initiative.objects.get(pk=initiative_id)
        context = self.get_context_data()
        community = context['profile'].get_first_geo_ten_community()
        messages_qs = initiative.initiative_messages.all().order_by('created_at')
        paginator = Paginator(messages_qs, self.MESSAGES_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        profile = context['profile']
        user_checked_initiative = profile.did_user_check_initiative(initiative=initiative)
        user_resolution_for_initiative = profile.get_user_resolution_for_initiative(initiative=initiative)
        agree_users = initiative.get_agree_users()
        reject_users = initiative.get_reject_users()
        extra_context = {
            'community': community,
            'initiative': initiative,
            'page_obj': page_obj,
            'user_checked_initiative': user_checked_initiative,
            'user_resolution_for_initiative': user_resolution_for_initiative,
            'agree_users': agree_users,
            'reject_users': reject_users,
        }
        context.update(extra_context)
        response = render(request, 'veche_initiative.html', context=context)
        return response

    def post(self, request, *args, **kwargs):
        initiative_id = kwargs.get('initiative_id')
        response_400 = self._check_initiative(initiative_id, is_resp_http=False)
        if response_400:
            return response_400

        initiative = Initiative.objects.get(pk=initiative_id)

        initiative_closed_400 = self._check_if_initiative_closed(initiative=initiative)
        if initiative_closed_400:
            return initiative_closed_400

        message_empty_400 = self._check_if_message_empty(request=request)
        if message_empty_400:
            return message_empty_400

        user_checked_initiative_400 = self._check_if_user_checked_initiative(initiative=initiative)
        if user_checked_initiative_400:
            return user_checked_initiative_400

        message_text = escape(request.POST.get('message', ''))
        new_message = MessageInitiative.objects.create(initiative=initiative, author=request.user, message=message_text)

        messages_qs = initiative.initiative_messages.all().order_by('created_at')
        paginator = Paginator(messages_qs, self.MESSAGES_ON_PAGE)
        data = {
            'pageNum': paginator.num_pages,
            'message_id': new_message.pk
        }
        return JsonResponse(data, status=200)


class ResolutionInitiativeView(InitiativeViewMixis, CustomTemplateViewMixin, TemplateView):
    AGREE_URL_ALIAS = 'agree_initiative'
    REJECT_URL_ALIAS = 'reject_initiative'

    def post(self, request, *args, **kwargs):
        initiative_id = kwargs.get('initiative_id')
        response_400 = self._check_initiative(initiative_id, is_resp_http=False)
        if response_400:
            return response_400

        initiative = Initiative.objects.get(pk=initiative_id)

        initiative_closed_400 = self._check_if_initiative_closed(initiative=initiative)
        if initiative_closed_400:
            return initiative_closed_400

        user_checked_initiative_400 = self._check_if_user_checked_initiative(initiative=initiative)
        if user_checked_initiative_400:
            return user_checked_initiative_400

        current_url_alias = request.resolver_match.url_name
        if current_url_alias == self.AGREE_URL_ALIAS:
            ResolutionInitiative.objects.create(author=request.user,
                                                resolution=ResolutionInitiative.RESOLUTION_AGREED_KEY,
                                                initiative=initiative)
        if current_url_alias == self.REJECT_URL_ALIAS:
            message_empty_400 = self._check_if_message_empty(request=request)
            if message_empty_400:
                return message_empty_400

            message_text = escape(request.POST.get('message', ''))
            ResolutionInitiative.objects.create(author=request.user,
                                                resolution=ResolutionInitiative.RESOLUTION_REJECTED_KEY,
                                                initiative=initiative,
                                                message=message_text)

        return JsonResponse({}, status=200)
