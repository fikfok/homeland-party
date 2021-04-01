import uuid
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.db import models
from safedelete.models import SafeDeleteModel


def invite_default_expire_at() -> datetime:
    """
    Значение по-умолчанию даты истекания срока годности приглашения
    :return: дата и время истечения срока годности приглашения
    """
    return datetime.now() + Invite.EXPIRE_PERIOD_HOURS


class Invite(SafeDeleteModel, models.Model):
    # Период, после которого приглашение протухает
    EXPIRE_PERIOD_HOURS = timedelta(hours=24)

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now=True, db_index=True)
    email = models.EmailField()
    is_activated = models.BooleanField(default=False, verbose_name='Профиль активирован')
    expire_at = models.DateTimeField(default=invite_default_expire_at)
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    password_changed = models.BooleanField(default=False, verbose_name='Пароль изменён')

    def __str__(self):
        return f'{self.email} ({self.code})'
