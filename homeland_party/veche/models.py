from django.contrib.auth import get_user_model
from django.db import models
from safedelete.models import SafeDeleteModel


class Community(SafeDeleteModel, models.Model):
    COMMUNITY_TYPE_TEN_KEY = 'ten'
    COMMUNITY_TYPE_TEN_LABEL = 'десятка'

    COMMUNITY_TYPE_CHOICES = (
        (COMMUNITY_TYPE_TEN_KEY, COMMUNITY_TYPE_TEN_LABEL),
    )

    MAX_PARTICIPANTS = {
        COMMUNITY_TYPE_TEN_KEY: 10,
    }

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True, db_index=True)
    type = models.CharField(verbose_name='Тип сообщества', choices=COMMUNITY_TYPE_CHOICES, max_length=50)
    max_participants = models.PositiveIntegerField(verbose_name="Максимальное количество дочерних элементов")

    def __str__(self):
        community_labels = {k: v for k, v in self.COMMUNITY_TYPE_CHOICES}
        current_label = community_labels[self.type]
        current_label = current_label.capitalize()
        return f'{current_label}. Автор: {self.author.username} (id = {self.author.pk})'
