from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.feedbacks.serializers import FeedbackSerializer
from feedbacks.models import Feedback


class FeedbacksViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().select_related("user")
