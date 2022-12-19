from rest_framework.routers import DefaultRouter

from api.feedbacks.views import FeedbacksViewSet


router = DefaultRouter()
router.register(r'feedbacks', FeedbacksViewSet, basename="api-feedbacks")
urlpatterns = router.urls
