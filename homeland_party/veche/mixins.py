from django.utils.html import escape
from typing import Union

from django.http import HttpResponse, JsonResponse

from veche.models import Initiative


class InitiativeViewMixis:
    def _check_initiative(self, initiative_id, is_resp_http=True) -> Union[HttpResponse, JsonResponse]:
        result = None
        try:
            initiative = Initiative.objects.get(pk=initiative_id)
        except Exception:
            msg = 'Инициатива не найдена'
            result = HttpResponse(msg, status=400) if is_resp_http else JsonResponse({'message': msg}, status=400)
        else:
            profile = self._get_profile()
            if not initiative.does_user_have_access(profile):
                msg = 'У вас нет доступа к инициативе'
                result = HttpResponse(msg, status=400) if is_resp_http else JsonResponse({'message': msg}, status=400)
        return result

    def _check_if_initiative_closed(self, initiative):
        result = None
        if initiative.status != Initiative.INITIATIVE_STATUS_OPEN_KEY:
            result = JsonResponse({'message': 'Инициатива закрыта. Добавлять сообщения нельзя'}, status=400)
        return result

    def _check_if_message_empty(self, request):
        result = None
        message_text = escape(request.POST.get('message', ''))
        if len(message_text.replace(' ', '')) == 0:
            result = JsonResponse({'message': 'Нельзя добавить пустое сообщение'}, status=400)
        return result

    def _check_if_user_checked_initiative(self, initiative):
        result = None
        context = self.get_context_data()
        profile = context['profile']
        user_checked_initiative = profile.did_user_check_initiative(initiative=initiative)
        if user_checked_initiative:
            result = JsonResponse({'message': 'Вы уже проголосовали за инициативу'}, status=400)
        return result
