from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.validators import MaxValueValidator
from django.db import models

from mystore.mixins.model_mixins import PKMixin


class Feedback(PKMixin):
    text = models.TextField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=(MaxValueValidator(5), )
    )

    def __str__(self):
        return f"{self.text[:40]} | {self.user} | {self.rating}"

    @classmethod
    def get_feedbacks_cache(cls):
        return cache.get_or_set("feedbacks", Feedback.objects.all())
